import type { PageServerLoad } from './$types';
import { getSecurityIncidentsFromFirebase, getCustomerByIdFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async () => {
    try {
        const rawIncidents = await getSecurityIncidentsFromFirebase();
        const incidents = await Promise.all(rawIncidents.map(async (inc) => {
            const customer = await getCustomerByIdFromFirebase(inc.customerId);
            return {
                id: inc.id,
                card: inc.cardNumber,
                atmId: 'ATM_TERMINAL_01',
                status: inc.status,
                attemptNumber: 1,
                createdAt: inc.timestamp,
                capturedImage: inc.attemptedImageUrl,
                ownerName: customer?.name || 'Account Owner',
                ownerEmail: customer?.email || 'Registered Email'
            };
        }));

        return { incidents };
    } catch (e) {
        console.error("Firebase RTDB Error loading security incidents:", e);
        return { incidents: [] };
    }
};
