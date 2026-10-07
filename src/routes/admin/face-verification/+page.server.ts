import type { PageServerLoad } from './$types';
import { getFaceVerificationsFromFirebase, getCustomersFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async () => {
    try {
        const [verifications, customers] = await Promise.all([
            getFaceVerificationsFromFirebase().catch(() => []),
            getCustomersFromFirebase().catch(() => [])
        ]);

        const customerMap = new Map(customers.map(c => [c.id, c]));

        const records = verifications.map(v => {
            const customer = customerMap.get(v.customerId);
            return {
                id: v.id,
                customerId: v.customerId,
                customerName: customer?.name || 'Account Owner',
                email: customer?.email || 'Registered Email',
                cardNumber: v.cardNumber,
                registeredFaceUrl: customer?.registeredFaceUrl || '',
                result: v.result,
                timestamp: v.timestamp
            };
        });

        const totalMatch = records.filter(r => r.result === 'MATCH').length;
        const totalMismatch = records.filter(r => r.result === 'MISMATCH').length;
        const totalSpoof = records.filter(r => r.result === 'SPOOF').length;

        return {
            records,
            stats: {
                total: records.length,
                totalMatch,
                totalMismatch,
                totalSpoof
            }
        };
    } catch (e) {
        console.error('[Firebase Face Verification Load Error]:', e);
        return { records: [], stats: { total: 0, totalMatch: 0, totalMismatch: 0, totalSpoof: 0 } };
    }
};
