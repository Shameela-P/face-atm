import type { PageServerLoad } from './$types';
import { getCustomersFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async () => {
    try {
        const customers = await getCustomersFromFirebase();
        const accounts = customers.map(c => ({
            id: c.id,
            accountNumber: c.accountNumber || 'ACC1001',
            customerName: c.fullName || c.name || 'Customer',
            email: c.email || '',
            cardNumber: c.cardNumber || 'N/A',
            bank: c.bank || 'SecureBank',
            branch: c.branch || 'Main Branch',
            balance: c.balance ?? 1000,
            status: c.status || 'ACTIVE',
            createdAt: c.createdAt ? c.createdAt.split('T')[0] : '2026-09-28'
        }));

        const totalBalance = accounts.reduce((sum, a) => sum + (a.balance ?? 0), 0);

        return {
            accounts,
            totalBalance
        };
    } catch (e) {
        console.error('[Firebase Load Error Accounts]:', e);
        return { accounts: [], totalBalance: 0 };
    }
};
