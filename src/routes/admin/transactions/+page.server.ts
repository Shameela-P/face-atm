import type { PageServerLoad } from './$types';
import { getAllTransactionsFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async () => {
    try {
        const rawTransactions = await getAllTransactionsFromFirebase();
        const transactions = rawTransactions.map(t => ({
            id: t.id,
            name: t.type === 'DEPOSIT' ? 'Deposit' : 'Withdrawal',
            accno: t.accountNumber,
            amount: t.amount,
            rdate: t.timestamp,
            userName: t.name,
            userId: t.customerId
        }));

        return { transactions };
    } catch (e) {
        console.error("Firebase RTDB Error loading admin transactions:", e);
        return { transactions: [] };
    }
};
