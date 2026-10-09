import { initializeApp, getApps, getApp } from 'firebase/app';
import { getDatabase, ref, get, set, push, child, update, query, orderByChild, equalTo } from 'firebase/database';
import { firebaseStorage } from './firebase';

const firebaseConfig = {
  apiKey: "AIzaSyAedUN6B2xOjgJsvpEL1R_aiXY4pV12JBA",
  authDomain: "face-76a11.firebaseapp.com",
  databaseURL: "https://face-76a11-default-rtdb.firebaseio.com",
  projectId: "face-76a11",
  storageBucket: "face-76a11.firebasestorage.app",
  messagingSenderId: "981118590426",
  appId: "1:981118590426:web:c05f36b38fc65fee0834e3",
  measurementId: "G-V6BCDE1BK1"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
export const firebaseRtdb = getDatabase(app);

export interface CustomerRecord {
    id: string; // CUST_...
    fullName: string;
    name?: string; // backward compatibility
    email: string;
    dob: string; // YYYY-MM-DD
    aadhaarNumber: string; // 12-digit unique
    mobile: number;
    address?: string;
    branch?: string;
    faceRecordId: string;
    registeredFaceUrl: string;
    status: 'ACTIVE' | 'SUSPENDED';
    createdAt: string;
    // Legacy fields for backward compatibility if queried:
    cardNumber?: string;
    accountNumber?: string;
    bank?: string;
    deposit?: number;
    balance?: number;
}

export interface BankAccountRecord {
    id: string; // ACC_...
    customerId: string;
    bankName: string;
    accountNumber: string;
    balance: number;
    status: 'ACTIVE' | 'SUSPENDED';
    createdAt: string;
}

export interface CardMapping {
    id: string; // CARD_...
    cardNumber: string; // 16-digit unique string
    customerId: string;
    accountId: string;
    status: string;
    createdAt: string;
}

export interface FaceRecord {
    id: string;
    customerId: string;
    embedding: string; // JSON stringified 128-d float array
    imageUrl: string;
    createdAt: string;
    status: string;
}

export interface TransactionRecord {
    id: string;
    customerId: string;
    cardNumber: string;
    accountId?: string;
    name: string;
    accountNumber: string;
    type: 'DEPOSIT' | 'WITHDRAWAL' | 'INITIAL_DEPOSIT';
    amount: number;
    balanceAfter: number;
    timestamp: string;
}

export interface SecurityIncidentRecord {
    id: string;
    customerId: string;
    cardNumber: string;
    attemptedImageUrl: string;
    incidentType: string;
    status: string;
    adminNotes?: string;
    timestamp: string;
}

export interface FaceVerificationRecord {
    id: string;
    customerId: string;
    cardNumber: string;
    result: 'MATCH' | 'MISMATCH' | 'SPOOF';
    timestamp: string;
}

export interface ComplaintRecord {
    id: string;
    customerId: string;
    customerName: string;
    email: string;
    category: string;
    subject: string;
    description: string;
    status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
    priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
    createdAt: string;
    adminResponse?: string;
    resolvedAt?: string;
}

export interface AdminAuditLogRecord {
    id: string;
    action: string;
    admin: string;
    targetType: string;
    targetId: string;
    details: string;
    timestamp: string;
}

export interface SystemSettingsRecord {
    appName: string;
    mlServiceUrl: string;
    sessionTimeoutMins: number;
    maxFailedAttempts: number;
    emailAlertsEnabled: boolean;
    incidentNotificationsEnabled: boolean;
}

// 1. Customer Operations
export async function getCustomersFromFirebase(): Promise<CustomerRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'customers'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            return Object.values(data) as CustomerRecord[];
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getCustomersFromFirebase:', err);
        return [];
    }
}

export async function getCustomerByIdFromFirebase(customerId: string): Promise<CustomerRecord | null> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, `customers/${customerId}`));
        if (snapshot.exists()) {
            const cust = snapshot.val() as CustomerRecord;
            cust.fullName = cust.fullName || cust.name || 'Customer';
            return cust;
        }
        return null;
    } catch (err) {
        console.error('[Firebase RTDB Error] getCustomerByIdFromFirebase:', err);
        return null;
    }
}

export async function getCustomerByAadhaarFromFirebase(aadhaarNumber: string): Promise<CustomerRecord | null> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, `customerByAadhaar/${aadhaarNumber}`));
        if (snapshot.exists()) {
            const indexData = snapshot.val();
            const customerId = typeof indexData === 'string' ? indexData : indexData.customerId;
            if (customerId) {
                return getCustomerByIdFromFirebase(customerId);
            }
        }

        // Direct scan fallback
        const customers = await getCustomersFromFirebase();
        const found = customers.find(c => c.aadhaarNumber === aadhaarNumber);
        return found || null;
    } catch (err) {
        console.error('[Firebase RTDB Error] getCustomerByAadhaarFromFirebase:', err);
        return null;
    }
}

export async function updateCustomerStatusInFirebase(customerId: string, status: 'ACTIVE' | 'SUSPENDED'): Promise<boolean> {
    try {
        const dbRef = ref(firebaseRtdb, `customers/${customerId}`);
        await update(dbRef, { status });
        await recordAuditLogInFirebase({
            action: status === 'SUSPENDED' ? 'CUSTOMER_SUSPENDED' : 'CUSTOMER_ACTIVATED',
            admin: 'sham@gmail.com',
            targetType: 'CUSTOMER',
            targetId: customerId,
            details: `Customer ${customerId} status changed to ${status}`
        });
        return true;
    } catch (err) {
        console.error('[Firebase RTDB Error] updateCustomerStatusInFirebase:', err);
        return false;
    }
}

// 2. Bank Accounts & Cards
export async function getBankAccountsByCustomerIdFromFirebase(customerId: string): Promise<BankAccountRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'bankAccounts'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            const accounts = Object.values(data) as BankAccountRecord[];
            return accounts.filter(a => a.customerId === customerId);
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getBankAccountsByCustomerIdFromFirebase:', err);
        return [];
    }
}

export async function getBankAccountByIdFromFirebase(accountId: string): Promise<BankAccountRecord | null> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, `bankAccounts/${accountId}`));
        if (snapshot.exists()) {
            return snapshot.val() as BankAccountRecord;
        }
        return null;
    } catch (err) {
        console.error('[Firebase RTDB Error] getBankAccountByIdFromFirebase:', err);
        return null;
    }
}

export async function getBankAccountByNumberAndBank(bankName: string, accountNumber: string): Promise<BankAccountRecord | null> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'bankAccounts'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            const accounts = Object.values(data) as BankAccountRecord[];
            const found = accounts.find(a => 
                a.bankName.toLowerCase().trim() === bankName.toLowerCase().trim() && 
                a.accountNumber.trim() === accountNumber.trim()
            );
            if (found) return found;
        }
        return null;
    } catch (err) {
        console.error('[Firebase RTDB Error] getBankAccountByNumberAndBank:', err);
        return null;
    }
}

export async function getCardsByCustomerIdFromFirebase(customerId: string): Promise<CardMapping[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'cards'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            const cards = Object.values(data) as CardMapping[];
            return cards.filter(c => c.customerId === customerId);
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getCardsByCustomerIdFromFirebase:', err);
        return [];
    }
}

export async function getCardMappingFromFirebase(cardNumber: string): Promise<CardMapping | null> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, `cards/${cardNumber}`));
        if (snapshot.exists()) {
            return snapshot.val() as CardMapping;
        }

        // Direct search fallback
        const allSnapshot = await get(child(dbRef, 'cards'));
        if (allSnapshot.exists()) {
            const data = allSnapshot.val();
            const cardObj = Object.values(data).find((c: any) => c.cardNumber === cardNumber);
            if (cardObj) return cardObj as CardMapping;
        }
        return null;
    } catch (err) {
        console.error('[Firebase RTDB Error] getCardMappingFromFirebase:', err);
        return null;
    }
}

export async function generateUniqueCardNumber(): Promise<string> {
    const dbRef = ref(firebaseRtdb);
    let isUnique = false;
    let newCardNumber = '';
    let tries = 0;

    while (!isUnique && tries < 20) {
        tries++;
        // 7-digit unique card number (1000000 to 9999999)
        newCardNumber = Math.floor(1000000 + Math.random() * 9000000).toString();

        const checkSnap = await get(child(dbRef, `cards/${newCardNumber}`));
        if (!checkSnap.exists()) {
            isUnique = true;
        }
    }
    return newCardNumber;
}

export async function getCardsCountFromFirebase(): Promise<number> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'cards'));
        if (snapshot.exists()) {
            return Object.keys(snapshot.val()).length;
        }
        return 0;
    } catch (err) {
        console.error('[Firebase RTDB Error] getCardsCountFromFirebase:', err);
        return 0;
    }
}

export async function getCustomerByCardFromFirebase(cardNumber: string): Promise<{ customer: CustomerRecord; card: CardMapping; account?: BankAccountRecord } | null> {
    const cardMap = await getCardMappingFromFirebase(cardNumber);
    if (!cardMap) return null;
    const customer = await getCustomerByIdFromFirebase(cardMap.customerId);
    if (!customer) return null;

    let account: BankAccountRecord | undefined;
    if (cardMap.accountId) {
        const acc = await getBankAccountByIdFromFirebase(cardMap.accountId);
        if (acc) account = acc;
    }

    return { customer, card: cardMap, account };
}

export async function getFaceRecordByCustomerIdFromFirebase(customerId: string): Promise<FaceRecord | null> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'faceRecords'));
        if (snapshot.exists()) {
            const records = snapshot.val();
            for (const key of Object.keys(records)) {
                if (records[key].customerId === customerId) {
                    return records[key] as FaceRecord;
                }
            }
        }
        return null;
    } catch (err) {
        console.error('[Firebase RTDB Error] getFaceRecordByCustomerIdFromFirebase:', err);
        return null;
    }
}

// 3. New Customer & Bank Account Registration Workflows

export async function registerCustomerWithAadhaarInFirebase(params: {
    fullName: string;
    email: string;
    dob: string;
    aadhaarNumber: string;
    mobile: number;
    bankName: string;
    accountNumber: string;
    registeredFaceUrl: string;
    embedding: number[];
}): Promise<{ success: boolean; customerId?: string; cardNumber?: string; error?: string }> {
    try {
        // Rule 1: Validate 12-digit Aadhaar Number format & uniqueness
        if (!/^[0-9]{12}$/.test(params.aadhaarNumber)) {
            return { success: false, error: 'Aadhaar number must contain exactly 12 digits.' };
        }
        const cleanAadhaar = params.aadhaarNumber;

        const existingCustomer = await getCustomerByAadhaarFromFirebase(cleanAadhaar);
        if (existingCustomer) {
            return { success: false, error: 'A customer with this Aadhaar number already exists.' };
        }

        // Rule 2: Validate bank account uniqueness per bank
        const existingAcc = await getBankAccountByNumberAndBank(params.bankName, params.accountNumber);
        if (existingAcc) {
            return { success: false, error: `Bank account ${params.accountNumber} is already registered under ${params.bankName}.` };
        }

        // Rule 3: Auto-generate unique 16-digit ATM Card Number
        const cardNumber = await generateUniqueCardNumber();

        const customerId = 'CUST_' + Math.floor(100000 + Math.random() * 900000).toString();
        const accountId = 'ACC_' + Math.floor(100000 + Math.random() * 900000).toString();
        const cardId = 'CARD_' + Math.floor(100000 + Math.random() * 900000).toString();
        const faceRecordId = 'FACE_' + Math.floor(100000 + Math.random() * 900000).toString();
        const createdAt = new Date().toISOString();

        const customerData: CustomerRecord = {
            id: customerId,
            fullName: params.fullName,
            name: params.fullName,
            email: params.email,
            dob: params.dob,
            aadhaarNumber: cleanAadhaar,
            mobile: params.mobile,
            faceRecordId,
            registeredFaceUrl: params.registeredFaceUrl,
            status: 'ACTIVE',
            createdAt,
            cardNumber,
            accountNumber: params.accountNumber,
            bank: params.bankName,
            balance: 1000
        };

        const bankAccountData: BankAccountRecord = {
            id: accountId,
            customerId,
            bankName: params.bankName,
            accountNumber: params.accountNumber,
            balance: 1000, // default starting deposit
            status: 'ACTIVE',
            createdAt
        };

        const cardData: CardMapping = {
            id: cardId,
            cardNumber,
            customerId,
            accountId,
            status: 'ACTIVE',
            createdAt
        };

        const faceData: FaceRecord = {
            id: faceRecordId,
            customerId,
            embedding: JSON.stringify(params.embedding),
            imageUrl: params.registeredFaceUrl,
            createdAt,
            status: 'ACTIVE'
        };

        // Multi-location atomic write in Firebase Realtime Database
        const updates: Record<string, any> = {};
        updates[`/customers/${customerId}`] = customerData;
        updates[`/customerByAadhaar/${cleanAadhaar}`] = { customerId };
        updates[`/bankAccounts/${accountId}`] = bankAccountData;
        updates[`/bankAccountsByCustomer/${customerId}/${accountId}`] = true;
        updates[`/cards/${cardNumber}`] = cardData;
        updates[`/faceRecords/${faceRecordId}`] = faceData;

        await update(ref(firebaseRtdb), updates);

        await recordAuditLogInFirebase({
            action: 'CUSTOMER_CREATED',
            admin: 'sham@gmail.com',
            targetType: 'CUSTOMER',
            targetId: customerId,
            details: `Registered customer ${params.fullName} (Aadhaar: ${cleanAadhaar}) with card ${cardNumber}`
        });

        console.log(`[Firebase RTDB Success] Customer & Card registered cleanly in Firebase. Customer ID: ${customerId}, Card: ${cardNumber}`);
        return { success: true, customerId, cardNumber };
    } catch (err: any) {
        console.error('[Firebase RTDB Write Error] registerCustomerWithAadhaarInFirebase:', err);
        return { success: false, error: err?.message || 'Firebase Realtime Database atomic write operation failed.' };
    }
}

export async function addAdditionalBankAccountInFirebase(params: {
    customerId: string;
    bankName: string;
    accountNumber: string;
}): Promise<{ success: boolean; accountId?: string; cardNumber?: string; error?: string }> {
    try {
        const customer = await getCustomerByIdFromFirebase(params.customerId);
        if (!customer) {
            return { success: false, error: 'Customer profile not found in Firebase.' };
        }

        const existingAcc = await getBankAccountByNumberAndBank(params.bankName, params.accountNumber);
        if (existingAcc) {
            return { success: false, error: `Bank account ${params.accountNumber} is already registered under ${params.bankName}.` };
        }

        const cardNumber = await generateUniqueCardNumber();
        const accountId = 'ACC_' + Math.floor(100000 + Math.random() * 900000).toString();
        const cardId = 'CARD_' + Math.floor(100000 + Math.random() * 900000).toString();
        const createdAt = new Date().toISOString();

        const bankAccountData: BankAccountRecord = {
            id: accountId,
            customerId: params.customerId,
            bankName: params.bankName,
            accountNumber: params.accountNumber,
            balance: 1000,
            status: 'ACTIVE',
            createdAt
        };

        const cardData: CardMapping = {
            id: cardId,
            cardNumber,
            customerId: params.customerId,
            accountId,
            status: 'ACTIVE',
            createdAt
        };

        const updates: Record<string, any> = {};
        updates[`/bankAccounts/${accountId}`] = bankAccountData;
        updates[`/bankAccountsByCustomer/${params.customerId}/${accountId}`] = true;
        updates[`/cards/${cardNumber}`] = cardData;

        await update(ref(firebaseRtdb), updates);

        await recordAuditLogInFirebase({
            action: 'BANK_ACCOUNT_ADDED',
            admin: 'sham@gmail.com',
            targetType: 'BANK_ACCOUNT',
            targetId: accountId,
            details: `Added ${params.bankName} account ${params.accountNumber} for customer ${params.customerId}. Generated Card: ${cardNumber}`
        });

        return { success: true, accountId, cardNumber };
    } catch (err: any) {
        console.error('[Firebase RTDB Error] addAdditionalBankAccountInFirebase:', err);
        return { success: false, error: err?.message || 'Failed to add bank account to Firebase.' };
    }
}

// 4. ATM Transaction Operations
export async function processTransactionInFirebase(params: {
    customerId: string;
    cardNumber: string;
    type: 'WITHDRAWAL' | 'DEPOSIT';
    amount: number;
}): Promise<{ success: boolean; newBalance: number; error?: string }> {
    try {
        const cardMap = await getCardMappingFromFirebase(params.cardNumber);
        if (!cardMap) {
            return { success: false, newBalance: 0, error: 'Card not found in Firebase.' };
        }

        const customer = await getCustomerByIdFromFirebase(cardMap.customerId);
        if (!customer) {
            return { success: false, newBalance: 0, error: 'Customer account not found in Firebase.' };
        }

        let account: BankAccountRecord | null = null;
        if (cardMap.accountId) {
            account = await getBankAccountByIdFromFirebase(cardMap.accountId);
        }

        const currentBalance: number = account ? (account.balance ?? 0) : (customer.balance ?? 0);
        let newBalance: number = currentBalance;

        if (params.type === 'WITHDRAWAL') {
            if (currentBalance < params.amount) {
                return { success: false, newBalance: currentBalance, error: 'Insufficient funds for withdrawal.' };
            }
            newBalance = currentBalance - params.amount;
        } else if (params.type === 'DEPOSIT') {
            newBalance = currentBalance + params.amount;
        }

        const transactionId = 'TXN_' + Date.now();
        const timestamp = new Date().toISOString();

        const transactionData: TransactionRecord = {
            id: transactionId,
            customerId: cardMap.customerId,
            cardNumber: params.cardNumber,
            accountId: cardMap.accountId || '',
            name: customer.fullName || customer.name || 'Customer',
            accountNumber: account ? account.accountNumber : customer.accountNumber || '',
            type: params.type,
            amount: params.amount,
            balanceAfter: newBalance,
            timestamp
        };

        const updates: Record<string, any> = {};
        if (account) {
            updates[`/bankAccounts/${account.id}/balance`] = newBalance;
        }
        updates[`/customers/${cardMap.customerId}/balance`] = newBalance;
        updates[`/transactions/${transactionId}`] = transactionData;

        await update(ref(firebaseRtdb), updates);
        return { success: true, newBalance };
    } catch (err: any) {
        console.error('[Firebase RTDB Error] processTransactionInFirebase:', err);
        return { success: false, newBalance: 0, error: err?.message || 'Transaction update failed in Firebase.' };
    }
}

export async function getTransactionsByCustomerIdFromFirebase(customerId: string): Promise<TransactionRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'transactions'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            const txns = Object.values(data) as TransactionRecord[];
            return txns.filter(t => t.customerId === customerId).sort((a, b) => b.timestamp.localeCompare(a.timestamp));
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getTransactionsByCustomerIdFromFirebase:', err);
        return [];
    }
}

export async function getAllTransactionsFromFirebase(): Promise<TransactionRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'transactions'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            return (Object.values(data) as TransactionRecord[]).sort((a, b) => b.timestamp.localeCompare(a.timestamp));
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getAllTransactionsFromFirebase:', err);
        return [];
    }
}

// 5. Security Incidents & Face Verifications
export async function recordSecurityIncidentInFirebase(params: {
    customerId: string;
    cardNumber: string;
    attemptedImageUrl: string;
    incidentType: string;
    status?: string;
}): Promise<{ success: boolean; incidentId: string }> {
    try {
        const incidentId = 'INC_' + Date.now();
        const timestamp = new Date().toISOString();

        const incidentData: SecurityIncidentRecord = {
            id: incidentId,
            customerId: params.customerId,
            cardNumber: params.cardNumber,
            attemptedImageUrl: params.attemptedImageUrl,
            incidentType: params.incidentType,
            status: params.status || 'UNAUTHORIZED_ATTEMPT',
            timestamp
        };

        const dbRef = ref(firebaseRtdb, `securityIncidents/${incidentId}`);
        await set(dbRef, incidentData);

        await recordFaceVerificationInFirebase({
            customerId: params.customerId,
            cardNumber: params.cardNumber,
            result: params.incidentType === 'SPOOF_DETECTED' ? 'SPOOF' : 'MISMATCH'
        });

        return { success: true, incidentId };
    } catch (err) {
        console.error('[Firebase RTDB Error] recordSecurityIncidentInFirebase:', err);
        return { success: false, incidentId: '' };
    }
}

export async function updateSecurityIncidentStatusInFirebase(incidentId: string, status: string, adminNotes?: string): Promise<boolean> {
    try {
        const dbRef = ref(firebaseRtdb, `securityIncidents/${incidentId}`);
        await update(dbRef, { status, adminNotes: adminNotes || 'Reviewed by Admin' });
        await recordAuditLogInFirebase({
            action: 'SECURITY_INCIDENT_REVIEWED',
            admin: 'sham@gmail.com',
            targetType: 'INCIDENT',
            targetId: incidentId,
            details: `Incident ${incidentId} status updated to ${status}`
        });
        return true;
    } catch (err) {
        console.error('[Firebase RTDB Error] updateSecurityIncidentStatusInFirebase:', err);
        return false;
    }
}

export async function getSecurityIncidentsFromFirebase(): Promise<SecurityIncidentRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'securityIncidents'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            return (Object.values(data) as SecurityIncidentRecord[]).sort((a, b) => b.timestamp.localeCompare(a.timestamp));
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getSecurityIncidentsFromFirebase:', err);
        return [];
    }
}

export async function recordFaceVerificationInFirebase(params: {
    customerId: string;
    cardNumber: string;
    result: 'MATCH' | 'MISMATCH' | 'SPOOF';
}): Promise<void> {
    try {
        const verificationId = 'VERIF_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
        const timestamp = new Date().toISOString();
        const verificationData: FaceVerificationRecord = {
            id: verificationId,
            customerId: params.customerId,
            cardNumber: params.cardNumber,
            result: params.result,
            timestamp
        };
        await set(ref(firebaseRtdb, `faceVerifications/${verificationId}`), verificationData);
    } catch (err) {
        console.error('[Firebase RTDB Error] recordFaceVerificationInFirebase:', err);
    }
}

export async function getFaceVerificationsFromFirebase(): Promise<FaceVerificationRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'faceVerifications'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            return (Object.values(data) as FaceVerificationRecord[]).sort((a, b) => b.timestamp.localeCompare(a.timestamp));
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getFaceVerificationsFromFirebase:', err);
        return [];
    }
}

// 6. Complaints Management
export async function getComplaintsFromFirebase(): Promise<ComplaintRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'complaints'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            return (Object.values(data) as ComplaintRecord[]).sort((a, b) => b.createdAt.localeCompare(a.createdAt));
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getComplaintsFromFirebase:', err);
        return [];
    }
}

export async function createComplaintInFirebase(params: {
    customerId: string;
    customerName: string;
    email: string;
    category: string;
    subject: string;
    description: string;
    priority?: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
}): Promise<{ success: boolean; complaintId: string }> {
    try {
        const complaintId = 'CMP_' + Date.now();
        const createdAt = new Date().toISOString();
        const complaintData: ComplaintRecord = {
            id: complaintId,
            customerId: params.customerId,
            customerName: params.customerName,
            email: params.email,
            category: params.category,
            subject: params.subject,
            description: params.description,
            status: 'OPEN',
            priority: params.priority || 'MEDIUM',
            createdAt
        };

        await set(ref(firebaseRtdb, `complaints/${complaintId}`), complaintData);
        return { success: true, complaintId };
    } catch (err) {
        console.error('[Firebase RTDB Error] createComplaintInFirebase:', err);
        return { success: false, complaintId: '' };
    }
}

export async function updateComplaintInFirebase(params: {
    complaintId: string;
    status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
    adminResponse?: string;
    priority?: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
}): Promise<boolean> {
    try {
        const dbRef = ref(firebaseRtdb, `complaints/${params.complaintId}`);
        const updates: Record<string, any> = {
            status: params.status,
            adminResponse: params.adminResponse || ''
        };
        if (params.priority) updates.priority = params.priority;
        if (params.status === 'RESOLVED' || params.status === 'CLOSED') {
            updates.resolvedAt = new Date().toISOString();
        }
        await update(dbRef, updates);

        await recordAuditLogInFirebase({
            action: 'COMPLAINT_UPDATED',
            admin: 'sham@gmail.com',
            targetType: 'COMPLAINT',
            targetId: params.complaintId,
            details: `Complaint ${params.complaintId} updated to status ${params.status}`
        });
        return true;
    } catch (err) {
        console.error('[Firebase RTDB Error] updateComplaintInFirebase:', err);
        return false;
    }
}

// 7. Admin Audit Logs & Settings
export async function recordAuditLogInFirebase(params: {
    action: string;
    admin: string;
    targetType: string;
    targetId: string;
    details: string;
}): Promise<void> {
    try {
        const logId = 'LOG_' + Date.now();
        const timestamp = new Date().toISOString();
        const logData: AdminAuditLogRecord = {
            id: logId,
            action: params.action,
            admin: params.admin,
            targetType: params.targetType,
            targetId: params.targetId,
            details: params.details,
            timestamp
        };
        await set(ref(firebaseRtdb, `adminAuditLogs/${logId}`), logData);
    } catch (err) {
        console.error('[Firebase RTDB Error] recordAuditLogInFirebase:', err);
    }
}

export async function getAuditLogsFromFirebase(): Promise<AdminAuditLogRecord[]> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'adminAuditLogs'));
        if (snapshot.exists()) {
            const data = snapshot.val();
            return (Object.values(data) as AdminAuditLogRecord[]).sort((a, b) => b.timestamp.localeCompare(a.timestamp));
        }
        return [];
    } catch (err) {
        console.error('[Firebase RTDB Error] getAuditLogsFromFirebase:', err);
        return [];
    }
}

export async function getSettingsFromFirebase(): Promise<SystemSettingsRecord> {
    try {
        const dbRef = ref(firebaseRtdb);
        const snapshot = await get(child(dbRef, 'settings'));
        if (snapshot.exists()) {
            return snapshot.val() as SystemSettingsRecord;
        }
        return {
            appName: 'Secure ATM Facial Verification System',
            mlServiceUrl: 'http://localhost:8000',
            sessionTimeoutMins: 15,
            maxFailedAttempts: 3,
            emailAlertsEnabled: true,
            incidentNotificationsEnabled: true
        };
    } catch (err) {
        return {
            appName: 'Secure ATM Facial Verification System',
            mlServiceUrl: 'http://localhost:8000',
            sessionTimeoutMins: 15,
            maxFailedAttempts: 3,
            emailAlertsEnabled: true,
            incidentNotificationsEnabled: true
        };
    }
}

export async function updateSettingsInFirebase(settings: Partial<SystemSettingsRecord>): Promise<boolean> {
    try {
        const dbRef = ref(firebaseRtdb, 'settings');
        await update(dbRef, settings);
        await recordAuditLogInFirebase({
            action: 'SETTINGS_CHANGED',
            admin: 'sham@gmail.com',
            targetType: 'SYSTEM',
            targetId: 'settings',
            details: 'System configuration settings updated'
        });
        return true;
    } catch (err) {
        console.error('[Firebase RTDB Error] updateSettingsInFirebase:', err);
        return false;
    }
}
