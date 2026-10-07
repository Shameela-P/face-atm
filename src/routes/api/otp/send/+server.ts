import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { canSendOtp, storeOtp } from '$lib/server/otpStore';
import { sendOtpEmail } from '$lib/server/email';
import crypto from 'crypto';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const body = await request.json();
        const email = body.email?.toString().trim();

        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            return json({ 
                success: false, 
                error: 'Valid email address is required.' 
            }, { status: 400 });
        }

        // 1. Rate Limiting Check for OTP Send
        const rateCheck = canSendOtp(email);
        if (!rateCheck.allowed) {
            return json({ 
                success: false, 
                error: rateCheck.error || 'Too many OTP requests. Please wait before requesting another OTP.' 
            }, { status: rateCheck.status || 429 });
        }

        // 2. Generate cryptographically secure 6-digit OTP server-side
        const otpNum = crypto.randomInt(0, 1000000);
        const otp = String(otpNum).padStart(6, '0');

        // 3. Attempt sending real Email OTP via Twilio REST API
        const emailResult = await sendOtpEmail(email, otp);

        if (!emailResult.success) {
            return json({ 
                success: false, 
                error: emailResult.error || 'Email service is not configured.' 
            }, { status: 400 });
        }

        // 4. Store hashed OTP temporarily on server side (5 minute expiry, max 30 attempts)
        storeOtp(email, otp);

        const emailParts = email.split('@');
        const maskedEmail = `${emailParts[0].substring(0, 2)}******@${emailParts[1]}`;

        // MUST NEVER EXPOSE THE OTP IN THE API RESPONSE!
        return json({
            success: true,
            maskedEmail,
            expiresIn: 300,
            message: `OTP sent successfully.`
        });
    } catch (err: any) {
        console.error('[SERVER ERROR] /api/otp/send:', err);
        return json({ success: false, error: 'Server error generating OTP.' }, { status: 500 });
    }
};
