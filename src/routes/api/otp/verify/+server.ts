import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { verifyOtp } from '$lib/server/otpStore';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const body = await request.json();
        const mobile = body.mobile?.toString().trim();
        const otp = body.otp?.toString().trim();

        if (!mobile || !/^[6-9][0-9]{9}$/.test(mobile)) {
            return json({ success: false, error: 'Mobile number must be a valid 10-digit Indian mobile number.' }, { status: 400 });
        }

        if (!otp || !/^[0-9]{4}$/.test(otp)) {
            return json({ success: false, error: 'OTP must be exactly 4 numeric digits.' }, { status: 400 });
        }

        const res = verifyOtp(mobile, otp);

        if (!res.success) {
            return json({ success: false, error: res.error || 'Invalid OTP. Please enter the correct OTP.' }, { status: res.status || 400 });
        }

        return json({
            success: true,
            message: 'Mobile number verified successfully.'
        });
    } catch (err: any) {
        return json({ success: false, error: 'Server error verifying OTP.' }, { status: 500 });
    }
};
