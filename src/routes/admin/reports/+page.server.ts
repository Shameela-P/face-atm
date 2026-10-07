import type { PageServerLoad } from './$types';
import { 
    getCustomersFromFirebase, 
    getAllTransactionsFromFirebase, 
    getSecurityIncidentsFromFirebase, 
    getComplaintsFromFirebase,
    getFaceVerificationsFromFirebase
} from '$lib/server/firebaseDb';

export const load: PageServerLoad = async () => {
    try {
        const [customers, transactions, incidents, complaints, verifications] = await Promise.all([
            getCustomersFromFirebase().catch(() => []),
            getAllTransactionsFromFirebase().catch(() => []),
            getSecurityIncidentsFromFirebase().catch(() => []),
            getComplaintsFromFirebase().catch(() => []),
            getFaceVerificationsFromFirebase().catch(() => [])
        ]);

        const totalDeposits = transactions.filter(t => t.type === 'DEPOSIT').reduce((sum, t) => sum + t.amount, 0);
        const totalWithdrawals = transactions.filter(t => t.type === 'WITHDRAWAL').reduce((sum, t) => sum + t.amount, 0);

        return {
            reportSummary: {
                totalCustomers: customers.length,
                totalTransactions: transactions.length,
                totalDeposits,
                totalWithdrawals,
                securityIncidentsCount: incidents.length,
                verificationsCount: verifications.length,
                complaintsCount: complaints.length
            },
            customers: customers.map(c => ({
                id: c.id,
                name: c.name,
                email: c.email,
                card: c.cardNumber,
                account: c.accountNumber,
                balance: c.balance,
                createdAt: c.createdAt
            })),
            transactions: transactions.map(t => ({
                id: t.id,
                customerId: t.customerId,
                name: t.name,
                type: t.type,
                amount: t.amount,
                balanceAfter: t.balanceAfter,
                timestamp: t.timestamp
            })),
            incidents: incidents.map(i => ({
                id: i.id,
                customerId: i.customerId,
                card: i.cardNumber,
                type: i.incidentType,
                status: i.status,
                timestamp: i.timestamp
            }))
        };
    } catch (e) {
        console.error('[Firebase Reports Load Error]:', e);
        return {
            reportSummary: {
                totalCustomers: 0,
                totalTransactions: 0,
                totalDeposits: 0,
                totalWithdrawals: 0,
                securityIncidentsCount: 0,
                verificationsCount: 0,
                complaintsCount: 0
            },
            customers: [],
            transactions: [],
            incidents: []
        };
    }
};
