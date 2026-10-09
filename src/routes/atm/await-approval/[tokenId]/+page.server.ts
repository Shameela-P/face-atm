import { error, redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApprovalRequest, consumeApproval, incrementApprovalOtpAttempts } from '$lib/server/approvalDb';
import crypto from 'crypto';

export const load: PageServerLoad = async ({ params, cookies }) => {
    const { tokenId } = params;
    const request = await getApprovalRequest(tokenId);
    if (!request) throw error(404, 'Approval request not found');

    const uidStr = cookies.get('atm_session_uid');
    if (!uidStr || request.customerId !== uidStr) {
        throw redirect(303, '/atm');
    }

    if (request.status === 'REJECTED') {
        cookies.delete('atm_session_uid', { path: '/' });
        cookies.delete('atm_session_card', { path: '/' });
        const encodedMsg = encodeURIComponent("Transaction Rejected! The account owner has denied this request. No withdrawal was performed. Please contact your bank if you need assistance.");
        throw redirect(303, `/atm?error=${encodedMsg}`);
    }

    return {
        request: {
            status: request.status,
            maxAmount: request.maxAmount
        }
    };
};

export const actions: Actions = {
    verifyOtp: async ({ request, params, cookies }) => {
        const { tokenId } = params;
        const appReq = await getApprovalRequest(tokenId);
        if (!appReq) return fail(404, { error: 'Request not found' });
        
        if (appReq.status === 'REJECTED') {
            return fail(403, { error: 'Transaction rejected by account owner.' });
        }
        if (appReq.status !== 'APPROVED') {
            return fail(400, { error: 'Awaiting owner approval.' });
        }

        const data = await request.formData();
        const enteredOtpRaw = data.get('otp')?.toString() || '';
        const enteredOtp = enteredOtpRaw.replace(/[^0-9]/g, '');
        
        if (!enteredOtp) return fail(400, { error: 'OTP is required' });

        const currentAttempts = appReq.otpAttempts || 0;
        if (currentAttempts >= 3) {
            return fail(403, { error: 'Maximum OTP attempts exceeded. Transaction cancelled.' });
        }

        if (!appReq.otpHash || !appReq.otpExpiry) {
            return fail(500, { error: 'OTP validation error.' });
        }

        if (new Date(appReq.otpExpiry) < new Date()) {
            return fail(400, { error: 'OTP has expired.' });
        }

        const hashedEnteredOtp = crypto.createHash('sha256').update(enteredOtp).digest('hex');
        
        if (hashedEnteredOtp !== appReq.otpHash) {
            await incrementApprovalOtpAttempts(tokenId, currentAttempts);
            return fail(400, { error: 'Incorrect OTP.' });
        }

        // Consume approval token so it can't be reused
        await consumeApproval(tokenId);

        // Grant ATM Authorization
        cookies.set('atm_authenticated', 'true', { path: '/', httpOnly: true, sameSite: 'lax', maxAge: 60 * 15 });
        cookies.set('atm_authorized_amount', appReq.maxAmount?.toString() || '0', { path: '/', httpOnly: true, sameSite: 'lax', maxAge: 60 * 15 });
        cookies.set('atm_authorized_token', tokenId, { path: '/', httpOnly: true, sameSite: 'lax', maxAge: 60 * 15 });

        throw redirect(303, '/atm/transaction');
    }
};
