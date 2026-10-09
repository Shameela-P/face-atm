import { fail, redirect, isRedirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getCustomerByIdFromFirebase, processTransactionInFirebase, getTransactionsByCustomerIdFromFirebase } from '$lib/server/firebaseDb';
import { sendTransactionReceiptEmail } from '$lib/server/email';

export const load: PageServerLoad = async ({ cookies }) => {
    const uidStr = cookies.get('atm_session_uid');
    const authenticated = cookies.get('atm_authenticated');
    
    if (!uidStr || authenticated !== 'true') {
        throw redirect(303, '/atm');
    }

    const authAmountStr = cookies.get('atm_authorized_amount');
    const authAmount = authAmountStr ? parseInt(authAmountStr, 10) : null;

    try {
        const customer = await getCustomerByIdFromFirebase(uidStr);
        if (!customer) {
            throw redirect(303, '/atm');
        }

        const txns = await getTransactionsByCustomerIdFromFirebase(uidStr);
        const transactions = txns.map(t => ({
            id: t.id,
            name: t.type === 'DEPOSIT' ? 'Deposit' : 'Withdrawal',
            accno: t.accountNumber,
            amount: t.amount,
            rdate: t.timestamp
        }));

        return {
            user: {
                id: customer.id,
                name: customer.fullName || customer.name || 'Customer',
                card: customer.cardNumber || '',
                accno: customer.accountNumber || '',
                deposit: customer.balance ?? 1000,
                email: customer.email || ''
            },
            accounts: [{
                id: customer.id,
                rid: customer.id,
                bank: customer.bank || 'SecureBank',
                account: customer.accountNumber || '',
                ifsc_code: 'SEC0001234',
                branch: customer.branch || 'Main Branch',
                deposit: (customer.balance ?? 1000).toString()
            }],
            transactions,
            authAmount
        };
    } catch (e) {
        if (isRedirect(e)) throw e;
        console.error("Firebase RTDB Error in ATM Transaction Load:", e);
        throw redirect(303, '/atm');
    }
};

export const actions: Actions = {
    withdraw: async ({ request, cookies }) => {
        const uidStr = cookies.get('atm_session_uid');
        const authenticated = cookies.get('atm_authenticated');
        if (!uidStr || authenticated !== 'true') throw redirect(303, '/atm');

        const formData = await request.formData();
        const amountStr = formData.get('amount')?.toString();
        const amount = parseInt(amountStr || '0', 10);

        if (isNaN(amount) || amount <= 0) {
            return fail(400, { error: 'Please enter a valid withdrawal amount.' });
        }

        const customer = await getCustomerByIdFromFirebase(uidStr);
        if (!customer) return fail(404, { error: 'Account not found in Firebase.' });

        const cardStr = cookies.get('atm_session_card') || customer.cardNumber || '';

        const authAmountStr = cookies.get('atm_authorized_amount');
        if (authAmountStr) {
            const authAmount = parseInt(authAmountStr, 10);
            if (amount !== authAmount) {
                return fail(403, { error: `You can only withdraw the exact amount authorized by the owner: ₹${authAmount.toLocaleString()}` });
            }
        }

        const result = await processTransactionInFirebase({
            customerId: uidStr,
            cardNumber: cardStr,
            type: 'WITHDRAWAL',
            amount
        });

        if (!result.success) {
            return fail(400, { error: result.error || 'Withdrawal failed.' });
        }

        // Send Transaction Receipt Email
        await sendTransactionReceiptEmail({
            toEmail: customer.email || '',
            ownerName: customer.fullName || customer.name || 'Customer',
            transactionId: 'TXN_' + Date.now(),
            type: 'WITHDRAWAL',
            amount,
            balance: result.newBalance,
            timestamp: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
            cardNumber: cardStr
        });

        cookies.delete('atm_session_uid', { path: '/' });
        cookies.delete('atm_session_card', { path: '/' });
        cookies.delete('atm_authenticated', { path: '/' });
        cookies.delete('atm_authorized_amount', { path: '/' });
        cookies.delete('atm_authorized_token', { path: '/' });

        return { success: true, message: `Withdrawal Successful! Thank you for using SecureATM. Have a great day!` };
    },

    deposit: async ({ request, cookies }) => {
        const uidStr = cookies.get('atm_session_uid');
        const authenticated = cookies.get('atm_authenticated');
        if (!uidStr || authenticated !== 'true') throw redirect(303, '/atm');

        const formData = await request.formData();
        const amountStr = formData.get('amount')?.toString();
        const amount = parseInt(amountStr || '0', 10);

        if (isNaN(amount) || amount <= 0) {
            return fail(400, { error: 'Please enter a valid deposit amount.' });
        }

        const customer = await getCustomerByIdFromFirebase(uidStr);
        if (!customer) return fail(404, { error: 'Account not found in Firebase.' });

        const cardStr = cookies.get('atm_session_card') || customer.cardNumber || '';

        const authAmountStr = cookies.get('atm_authorized_amount');
        if (authAmountStr) {
            const authAmount = parseInt(authAmountStr, 10);
            if (amount !== authAmount) {
                return fail(403, { error: `You can only deposit the exact amount authorized by the owner: ₹${authAmount.toLocaleString()}` });
            }
        }

        const result = await processTransactionInFirebase({
            customerId: uidStr,
            cardNumber: cardStr,
            type: 'DEPOSIT',
            amount
        });

        if (!result.success) {
            return fail(400, { error: result.error || 'Deposit failed.' });
        }

        // Send Transaction Receipt Email
        await sendTransactionReceiptEmail({
            toEmail: customer.email || '',
            ownerName: customer.fullName || customer.name || 'Customer',
            transactionId: 'TXN_' + Date.now(),
            type: 'DEPOSIT',
            amount,
            balance: result.newBalance,
            timestamp: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
            cardNumber: cardStr
        });

        cookies.delete('atm_session_uid', { path: '/' });
        cookies.delete('atm_session_card', { path: '/' });
        cookies.delete('atm_authenticated', { path: '/' });
        cookies.delete('atm_authorized_amount', { path: '/' });
        cookies.delete('atm_authorized_token', { path: '/' });

        return { success: true, message: `Deposit Successful! Thank you for using SecureATM. Have a great day!` };
    },

    logout: async ({ cookies }) => {
        cookies.delete('atm_session_uid', { path: '/' });
        cookies.delete('atm_session_card', { path: '/' });
        cookies.delete('atm_authenticated', { path: '/' });
        cookies.delete('atm_authorized_amount', { path: '/' });
        cookies.delete('atm_authorized_token', { path: '/' });
        throw redirect(303, '/atm');
    }
};
