import { fail, redirect, isRedirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getCustomerByIdFromFirebase, processTransactionInFirebase, getTransactionsByCustomerIdFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async ({ cookies }) => {
    const uidStr = cookies.get('atm_session_uid');
    const authenticated = cookies.get('atm_authenticated');
    
    if (!uidStr || authenticated !== 'true') {
        throw redirect(303, '/atm');
    }

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
            transactions
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

        const result = await processTransactionInFirebase({
            customerId: uidStr,
            cardNumber: cardStr,
            type: 'WITHDRAWAL',
            amount
        });

        if (!result.success) {
            return fail(400, { error: result.error || 'Withdrawal failed.' });
        }

        cookies.delete('atm_session_uid', { path: '/' });
        cookies.delete('atm_session_card', { path: '/' });
        cookies.delete('atm_authenticated', { path: '/' });

        return { success: true, message: `Withdrawal of ₹${amount.toLocaleString()} successful! New Balance: ₹${result.newBalance.toLocaleString()}` };
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

        const result = await processTransactionInFirebase({
            customerId: uidStr,
            cardNumber: cardStr,
            type: 'DEPOSIT',
            amount
        });

        if (!result.success) {
            return fail(400, { error: result.error || 'Deposit failed.' });
        }

        cookies.delete('atm_session_uid', { path: '/' });
        cookies.delete('atm_session_card', { path: '/' });
        cookies.delete('atm_authenticated', { path: '/' });

        return { success: true, message: `Deposit of ₹${amount.toLocaleString()} successful! New Balance: ₹${result.newBalance.toLocaleString()}` };
    },

    logout: async ({ cookies }) => {
        cookies.delete('atm_session_uid', { path: '/' });
        cookies.delete('atm_session_card', { path: '/' });
        cookies.delete('atm_authenticated', { path: '/' });
        throw redirect(303, '/atm');
    }
};
