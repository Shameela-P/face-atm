import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { verifyOtp, verifiedEmails } from '$lib/server/otpStore';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const body = await request.json();
        const email = body.email?.toString().trim();
        const otp = body.otp?.toString().trim();

        if (!email || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
            return json({ success: false, error: 'A valid email address is required.' }, { status: 400 });
        }

        if (!otp || !/^[0-9]{6}$/.test(otp)) {
            return json({ success: false, error: 'OTP must be exactly 6 numeric digits.' }, { status: 400 });
        }

        const res = verifyOtp(email, otp);

        if (!res.success) {
            return json({ success: false, error: res.error || 'Invalid OTP. Please enter the correct OTP.' }, { status: res.status || 400 });
        }

        // Add to verified sessions
        verifiedEmails.add(email);

        return json({
            success: true,
            message: 'Email verified successfully.'
        });
    } catch (err: any) {
        return json({ success: false, error: 'Server error verifying OTP.' }, { status: 500 });
    }
};
