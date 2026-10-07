import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { canSendOtp, storeOtp } from '$lib/server/otpStore';
import { sendOtpSms } from '$lib/server/sms';
import crypto from 'crypto';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const body = await request.json();
        const mobile = body.mobile?.toString().trim();

        if (!mobile || !/^[6-9][0-9]{9}$/.test(mobile)) {
            return json({ 
                success: false, 
                error: 'Mobile number must be a valid 10-digit Indian mobile number.' 
            }, { status: 400 });
        }

        // 1. Rate Limiting Check for OTP Send
        const rateCheck = canSendOtp(mobile);
        if (!rateCheck.allowed) {
            return json({ 
                success: false, 
                error: rateCheck.error || 'Too many OTP requests. Please wait before requesting another OTP.' 
            }, { status: rateCheck.status || 429 });
        }

        // 2. Generate cryptographically secure 4-digit OTP server-side
        const otpNum = crypto.randomInt(0, 10000);
        const otp = String(otpNum).padStart(4, '0');

        // 3. Attempt sending real SMS OTP via Twilio REST API
        const smsResult = await sendOtpSms(mobile, otp);

        if (!smsResult.success) {
            return json({ 
                success: false, 
                error: smsResult.error || 'SMS service is not configured. Please configure the SMS provider before sending OTP.' 
            }, { status: 400 });
        }

        // 4. Store hashed OTP temporarily on server side (5 minute expiry, max 30 attempts)
        storeOtp(mobile, otp);

        const maskedMobile = `+91******${mobile.slice(-4)}`;

        // MUST NEVER EXPOSE THE OTP IN THE API RESPONSE!
        return json({
            success: true,
            maskedMobile,
            expiresIn: 300,
            message: `OTP sent successfully.`
        });
    } catch (err: any) {
        return json({ success: false, error: 'Server error generating OTP.' }, { status: 500 });
    }
};
