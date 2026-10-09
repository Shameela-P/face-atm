import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { sendOtpEmail } from '$lib/server/email';
import { canSendOtp, storeOtp } from '$lib/server/otpStore';
import crypto from 'crypto';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const body = await request.json();
        const email = body.email?.toString().trim();

        if (!email || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
            return json({ 
                success: false, 
                error: 'A valid email address is required.' 
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

        // 3. Attempt sending real Email OTP via Resend API
        const emailResult = await sendOtpEmail(email, otp);

        if (!emailResult.success) {
            return json({ 
                success: false, 
                error: emailResult.error || 'Email service is not configured.' 
            }, { status: 400 });
        }

        // 4. Store hashed OTP temporarily on server side (5 minute expiry, max 30 attempts)
        storeOtp(email, otp);

        // Mask the email for the response
        const [localPart, domain] = email.split('@');
        const maskedLocal = localPart.length > 2 ? localPart.slice(0, 2) + '*'.repeat(localPart.length - 2) : '*'.repeat(localPart.length);
        const maskedEmail = `${maskedLocal}@${domain}`;

        return json({
            success: true,
            maskedEmail,
            expiresIn: 300,
            message: `OTP sent successfully via Email.`
        });
    } catch (err: any) {
        console.error('[SERVER ERROR] /api/otp/send:', err);
        return json({ success: false, error: 'Server error generating OTP.' }, { status: 500 });
    }
};
