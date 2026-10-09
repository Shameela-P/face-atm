import dotenv from 'dotenv';
import { Resend } from 'resend';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '.env') });

const resendApiKey = process.env.RESEND_API_KEY;
const resendFromEmail = process.env.OTP_FROM_EMAIL || process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';
const targetEmail = 'shameela5qts@gmail.com';

async function testResend() {
    console.log('Testing Email OTP via Resend...');
    
    if (!resendApiKey) {
        console.error('Missing RESEND_API_KEY in .env');
        process.exit(1);
    }

    const resend = new Resend(resendApiKey);
    const otp = '123456';

    try {
        const { data, error } = await resend.emails.send({
            from: resendFromEmail,
            to: [targetEmail],
            subject: "Your OTP Verification Code",
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
                    <div style="background-color: #0ea5e9; color: white; padding: 16px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h2 style="margin: 0;">SecureATM</h2>
                    </div>
                    
                    <div style="padding: 24px; color: #1e293b; line-height: 1.6; text-align: center;">
                        <p>Your verification code is:</p>
                        <h1 style="font-size: 36px; letter-spacing: 8px; color: #0f172a; margin: 20px 0;">${otp}</h1>
                        <p style="color: #64748b; font-size: 14px;">This code expires in 5 minutes.</p>
                        <p style="color: #64748b; font-size: 14px;">If you did not request this code, you can safely ignore this email.</p>
                    </div>
                </div>
            `
        });

        if (error) {
            console.error('API error:', error);
            process.exit(1);
        }

        console.log('API connection successful. Email OTP accepted by Resend provider.');
        console.log('Delivery ID:', data.id);
    } catch (e) {
        console.error('Error connecting to Resend API:');
        console.error(e);
        process.exit(1);
    }
}

testResend();
