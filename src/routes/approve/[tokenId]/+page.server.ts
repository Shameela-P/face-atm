import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApprovalRequest, updateApprovalRequestStatus, storeApprovalOtp } from '$lib/server/approvalDb';
import { getCustomerByIdFromFirebase } from '$lib/server/firebaseDb';
import { sendOtpEmail } from '$lib/server/email';
import crypto from 'crypto';

export const load: PageServerLoad = async ({ params }) => {
    const { tokenId } = params;
    const request = await getApprovalRequest(tokenId);
    
    if (!request) throw error(404, 'Invalid or expired approval link');

    const customer = await getCustomerByIdFromFirebase(request.customerId);
    
    return {
        tokenId,
        request: {
            ...request,
            customerName: customer?.name || 'Account Owner'
        }
    };
};

export const actions: Actions = {
    approve: async ({ params, request }) => {
        const { tokenId } = params;
        const appReq = await getApprovalRequest(tokenId);
        
        if (!appReq) return fail(404, { error: 'Request not found' });
        if (appReq.status !== 'PENDING') return fail(400, { error: 'Request is no longer pending.' });

        const data = await request.formData();
        const maxAmountStr = data.get('maxAmount')?.toString();
        const maxAmount = parseInt(maxAmountStr || '0', 10);

        if (isNaN(maxAmount) || maxAmount <= 0) {
            return fail(400, { error: 'Please enter a valid maximum amount.' });
        }

        const customer = await getCustomerByIdFromFirebase(appReq.customerId);
        if (!customer) return fail(404, { error: 'Customer not found.' });

        // Update status to APPROVED and set maxAmount
        await updateApprovalRequestStatus(tokenId, 'APPROVED', maxAmount);

        // Generate OTP
        const otp = Math.floor(100000 + Math.random() * 900000).toString();
        const otpHash = crypto.createHash('sha256').update(otp).digest('hex');

        await storeApprovalOtp(tokenId, otpHash, 5 * 60 * 1000); // 5 minutes expiry

        // Send OTP via Email
        await sendOtpEmail(customer.email, otp);

        return { success: true, message: 'Approval confirmed. An OTP has been sent to your email.' };
    }
};
