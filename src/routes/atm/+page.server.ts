import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { getCustomerByCardFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async ({ url }) => {
    return {
        successMessage: url.searchParams.get('success') || null,
        errorMessage: url.searchParams.get('error') || null
    };
};

export const actions = {
    default: async ({ request, cookies }) => {
        const data = await request.formData();
        const rawInput = data.get('cardNumber')?.toString() || '';
        const cardNumber = rawInput.replace(/\s+/g, '').replace(/-/g, '').trim();

        // Masked card number for secure diagnostic logging (e.g. **** **** **** 1234)
        const maskedCard = cardNumber.length >= 4 
            ? `**** **** **** ${cardNumber.slice(-4)}` 
            : '****';

        if (!cardNumber) {
            console.warn(`[ATM Auth] Rejection: Empty card number submitted.`);
            return fail(400, { error: 'Please enter your 16-digit ATM card number.', cardNumber: rawInput });
        }

        if (!/^\d{6,7}$/.test(cardNumber)) {
            console.warn(`[ATM Auth] Rejection: Invalid card number length/format: ${maskedCard}`);
            return fail(400, { error: 'ATM card number must be exactly 6 or 7 digits.', cardNumber: rawInput });
        }

        try {
            console.log(`[ATM Auth] Verifying card lookup in Firebase RTDB for: ${maskedCard}`);
            const result = await getCustomerByCardFromFirebase(cardNumber);

            if (!result) {
                console.warn(`[ATM Auth] Rejection: Card not found in Firebase: ${maskedCard}`);
                return fail(404, { error: 'Invalid card number. Please check your card details and try again.', cardNumber: rawInput });
            }

            const { customer, card } = result;

            if (card.status === 'BLOCKED' || card.status === 'INACTIVE' || card.status === 'SUSPENDED' || customer.status === 'SUSPENDED') {
                console.warn(`[ATM Auth] Rejection: Card ${maskedCard} is inactive/blocked (Card status: ${card.status}, Customer status: ${customer.status})`);
                return fail(403, { error: 'This ATM card is blocked or inactive. Please contact customer support.', cardNumber: rawInput });
            }

            // Set secure session cookies for ATM verification flow
            cookies.set('atm_session_card', cardNumber, { path: '/', maxAge: 60 * 15, httpOnly: true, sameSite: 'lax' });
            cookies.set('atm_session_uid', customer.id, { path: '/', maxAge: 60 * 15, httpOnly: true, sameSite: 'lax' });
            
            console.log(`[ATM Auth] Success: Card ${maskedCard} authenticated. Customer ID: ${customer.id}. Redirecting to /atm/face-scan`);
        } catch (e: any) {
            console.error(`[ATM Auth] Firebase RTDB Lookup Error for ${maskedCard}:`, e);
            return fail(500, { error: 'Failed to access Firebase Realtime Database. Check network or configuration.', cardNumber: rawInput });
        }

        // Redirect to live face verification flow
        throw redirect(303, '/atm/face-scan');
    }
} satisfies Actions;
