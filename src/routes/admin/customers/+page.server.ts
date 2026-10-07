import { fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { uploadImageToFirebaseStorage } from '$lib/server/firebase';
import { 
    getCustomersFromFirebase, 
    getCustomerByIdFromFirebase,
    getCustomerByAadhaarFromFirebase, 
    getBankAccountsByCustomerIdFromFirebase, 
    getBankAccountByNumberAndBank,
    getCardsByCustomerIdFromFirebase,
    registerCustomerWithAadhaarInFirebase, 
    addAdditionalBankAccountInFirebase,
    updateCustomerStatusInFirebase 
} from '$lib/server/firebaseDb';
import { generateFaceEmbedding, checkMlServiceHealth } from '$lib/server/mlService';
import { sendCardDeliveryEmail } from '$lib/server/email';
import { sendCardSms } from '$lib/server/sms';
import { isOtpVerified, clearOtp } from '$lib/server/otpStore';

export const load: PageServerLoad = async () => {
    try {
        const customersData = await getCustomersFromFirebase();
        const mlHealth = await checkMlServiceHealth();

        // Populate bank accounts and cards for each customer
        const customers = await Promise.all(customersData.map(async (c) => {
            const accounts = await getBankAccountsByCustomerIdFromFirebase(c.id);
            const cards = await getCardsByCustomerIdFromFirebase(c.id);

            const formattedAccounts = accounts.map(acc => {
                const card = cards.find(card => card.accountId === acc.id);
                return {
                    id: acc.id,
                    bankName: acc.bankName,
                    accountNumber: acc.accountNumber,
                    balance: acc.balance,
                    status: acc.status,
                    cardNumber: card ? card.cardNumber : 'N/A'
                };
            });

            // Mask Aadhaar format: XXXX XXXX 9012
            const cleanAadhaar = c.aadhaarNumber ? c.aadhaarNumber.replace(/\D/g, '') : '';
            const maskedAadhaar = cleanAadhaar.length === 12 
                ? `XXXX XXXX ${cleanAadhaar.slice(-4)}`
                : (cleanAadhaar || 'N/A');

            return {
                id: c.id,
                fullName: c.fullName || c.name || 'Customer',
                email: c.email,
                dob: c.dob || 'N/A',
                aadhaarNumber: c.aadhaarNumber || '',
                maskedAadhaar,
                mobile: c.mobile || 'N/A',
                status: c.status || 'ACTIVE',
                createdAt: c.createdAt ? c.createdAt.split('T')[0] : new Date().toISOString().split('T')[0],
                registeredFaceUrl: c.registeredFaceUrl,
                bankAccounts: formattedAccounts,
                accountCount: formattedAccounts.length,
                faceStatus: c.registeredFaceUrl ? 'Registered' : 'Pending'
            };
        }));

        return { 
            customers,
            mlOnline: mlHealth.online,
            todayDate: new Date().toISOString().split('T')[0]
        };
    } catch (e) {
        console.error("[Firebase Load Error]:", e);
        return { customers: [], mlOnline: false, todayDate: new Date().toISOString().split('T')[0] };
    }
};

export const actions: Actions = {
    registerCustomer: async ({ request }) => {
        const formData = await request.formData();
        
        const fullName = formData.get('fullName')?.toString().trim();
        const email = formData.get('email')?.toString().trim();
        const dob = formData.get('dob')?.toString().trim();
        const aadhaarNumber = formData.get('aadhaarNumber')?.toString().trim();
        const bankName = formData.get('bankName')?.toString().trim();
        const accountNumber = formData.get('accountNumber')?.toString().trim();
        const mobileStr = formData.get('mobile')?.toString().trim();
        const verifiedEmailStr = formData.get('verifiedEmail')?.toString().trim();
        const faceImageB64 = formData.get('faceImageB64')?.toString();

        // 1. SPECIFIC Field Validation (Never return generic error when single field missing)
        if (!fullName) {
            return fail(400, { error: 'Customer Full Name is required.' });
        }
        if (!email) {
            return fail(400, { error: 'Email Address is required.' });
        }
        if (!dob) {
            return fail(400, { error: 'Date of Birth is required.' });
        }
        if (!aadhaarNumber) {
            return fail(400, { error: 'Aadhaar Number is required.' });
        }
        if (!bankName) {
            return fail(400, { error: 'Bank Name is required.' });
        }
        if (!accountNumber) {
            return fail(400, { error: 'Bank Account Number is required.' });
        }
        if (!mobileStr) {
            return fail(400, { error: 'Mobile Number is required.' });
        }
        if (!faceImageB64) {
            return fail(400, { error: 'Original Owner Face Capture is required. Please capture face before registering.' });
        }

        // 2. Date of Birth Validation (NEVER ALLOW FUTURE DATE)
        const todayStr = new Date().toISOString().split('T')[0];
        if (dob > todayStr) {
            return fail(400, { error: 'Date of birth cannot be a future date.' });
        }

        // 3. Indian Mobile Number Format & Server-Side OTP Verification Check
        if (!/^[6-9][0-9]{9}$/.test(mobileStr)) {
            return fail(400, { error: 'Mobile number must be a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.' });
        }

        if (verifiedEmailStr && email !== verifiedEmailStr) {
            return fail(400, { error: 'Email address was modified after OTP verification. Please re-verify email address.' });
        }

        if (!isOtpVerified(email)) {
            return fail(400, { error: 'Email verification is required.' });
        }

        // 4. Aadhaar Validation (Exactly 12 numeric digits, numeric only)
        if (!/^[0-9]{12}$/.test(aadhaarNumber)) {
            return fail(400, { error: 'Aadhaar number must contain exactly 12 digits.' });
        }

        // Search Firebase for duplicate Aadhaar
        const existingAadhaarCustomer = await getCustomerByAadhaarFromFirebase(aadhaarNumber);
        if (existingAadhaarCustomer) {
            return fail(400, { error: 'This Aadhaar number is already registered.' });
        }

        // 5. Bank Account Uniqueness per Bank
        const existingBankAcc = await getBankAccountByNumberAndBank(bankName, accountNumber);
        if (existingBankAcc) {
            return fail(400, { error: 'Bank account number is already registered.' });
        }

        // 6. ML Face Processing (FastAPI MTCNN -> Liveness -> FaceNet 128-d vector)
        const mlResult = await generateFaceEmbedding(faceImageB64);
        if (!mlResult.success || !mlResult.embedding) {
            return fail(400, { error: mlResult.error || 'Face recognition service failed. Please position face correctly and try again.' });
        }

        const embedding = mlResult.embedding;
        const mobile = parseInt(mobileStr, 10);

        try {
            // Pre-generate temporary customer ID for storage path
            const tempCustomerId = 'CUST_' + Math.floor(100000 + Math.random() * 900000).toString();
            const storagePath = `face-images/registered/${tempCustomerId}/original-face.jpg`;
            let firebaseUrl = '';
            try {
                firebaseUrl = await uploadImageToFirebaseStorage(faceImageB64, storagePath);
            } catch (fbErr) {
                console.warn("[Firebase Storage] Registration upload fallback:", fbErr);
                firebaseUrl = storagePath;
            }

            // 7. Atomic Firebase Registration
            const fbResult = await registerCustomerWithAadhaarInFirebase({
                fullName,
                email,
                dob,
                aadhaarNumber,
                mobile,
                bankName,
                accountNumber,
                registeredFaceUrl: firebaseUrl,
                embedding
            });

            if (!fbResult.success || !fbResult.cardNumber) {
                return fail(400, { error: fbResult.error || 'Failed to complete customer registration in Firebase.' });
            }

            // Clean up OTP store for this email
            clearOtp(email);

            // 8. Send ATM Card Number SMS via Twilio to the VERIFIED customer mobile number
            const smsResult = await sendCardSms(mobileStr, fbResult.cardNumber);

            const cardSmsNotice = smsResult.success
                ? `Card number SMS delivered to +91******${mobileStr.slice(-4)} via Twilio.`
                : 'Customer registered successfully and ATM card generated, but card SMS delivery failed. Please retry card notification.';

            // 9. Send Card Delivery Notification Email to Customer
            const emailSuccess = await sendCardDeliveryEmail({
                toEmail: email,
                customerName: fullName,
                bankName,
                accountNumber,
                cardNumber: fbResult.cardNumber
            });

            const emailNotice = emailSuccess 
                ? 'Email delivered to ' + email
                : 'Card email delivery is pending because email service is not configured.';

            return { 
                success: true, 
                registrationComplete: true,
                customer: {
                    id: fbResult.customerId,
                    fullName,
                    email,
                    mobile: mobileStr,
                    cardNumber: fbResult.cardNumber,
                    maskedCard: '**** **** **** ' + fbResult.cardNumber.slice(-4),
                    bankName,
                    accountNumber,
                    cardSmsNotice,
                    emailNotice
                }
            };
        } catch (e: any) {
            console.error("Registration Server Error:", e);
            return fail(500, { error: `Registration error: ${e?.message || 'Unexpected server error'}` });
        }
    },

    retryCardNotification: async ({ request }) => {
        const formData = await request.formData();
        const customerId = formData.get('customerId')?.toString().trim();
        const cardNumber = formData.get('cardNumber')?.toString().trim();
        const mobileStr = formData.get('mobile')?.toString().trim();

        if (!customerId || !cardNumber || !mobileStr) {
            return fail(400, { error: 'Customer ID, Card Number, and Mobile Number are required.' });
        }

        const smsResult = await sendCardSms(mobileStr, cardNumber);
        if (!smsResult.success) {
            return fail(400, { error: smsResult.error || 'Failed to resend ATM card SMS notification.' });
        }

        return {
            success: true,
            message: `Card notification SMS resent successfully to +91******${mobileStr.slice(-4)}.`
        };
    },

    addBankAccount: async ({ request }) => {
        const formData = await request.formData();
        const customerId = formData.get('customerId')?.toString().trim();
        const bankName = formData.get('bankName')?.toString().trim();
        const accountNumber = formData.get('accountNumber')?.toString().trim();

        if (!customerId || !bankName || !accountNumber) {
            return fail(400, { error: 'Customer ID, Bank Name, and Account Number are required.' });
        }

        const existingBankAcc = await getBankAccountByNumberAndBank(bankName, accountNumber);
        if (existingBankAcc) {
            return fail(400, { error: 'Bank account number is already registered.' });
        }

        const result = await addAdditionalBankAccountInFirebase({
            customerId,
            bankName,
            accountNumber
        });

        if (!result.success || !result.cardNumber) {
            return fail(400, { error: result.error || 'Failed to add bank account to Firebase.' });
        }

        // Send email with new card details
        const customer = await getCustomerByIdFromFirebase(customerId);
        if (customer && customer.email) {
            await sendCardDeliveryEmail({
                toEmail: customer.email,
                customerName: customer.fullName || customer.name || 'Customer',
                bankName,
                accountNumber,
                cardNumber: result.cardNumber
            });
        }

        return {
            success: true,
            message: `New ${bankName} account added successfully for customer! Generated ATM Card: ${result.cardNumber}`
        };
    },

    toggleCustomerStatus: async ({ request }) => {
        const formData = await request.formData();
        const customerId = formData.get('customerId')?.toString();
        const newStatus = formData.get('status')?.toString() as 'ACTIVE' | 'SUSPENDED';

        if (!customerId || !newStatus) {
            return fail(400, { error: 'Customer ID and target status are required.' });
        }

        const success = await updateCustomerStatusInFirebase(customerId, newStatus);
        if (!success) {
            return fail(500, { error: 'Failed to update customer status in Firebase.' });
        }

        return { success: true, message: `Customer ${customerId} status updated to ${newStatus}.` };
    }
};
