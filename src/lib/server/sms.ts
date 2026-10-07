export interface SendSmsResult {
    success: boolean;
    error?: string;
}

import { env } from '$env/dynamic/private';

/**
 * Normalizes Indian 10-digit mobile number to E.164 format (+91XXXXXXXXXX)
 */
export function normalizeMobileToE164(mobile: string): string {
    const digits = mobile.replace(/\D/g, '');
    if (digits.length === 10) {
        return `+91${digits}`;
    }
    if (digits.length === 12 && digits.startsWith('91')) {
        return `+${digits}`;
    }
    return mobile.startsWith('+') ? mobile : `+${digits}`;
}

/**
 * Sends a 4-digit OTP SMS via Twilio SMS Provider API.
 * Uses TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER.
 * Never logs or returns the plaintext OTP.
 */
export async function sendOtpSms(mobile: string, otp: string): Promise<SendSmsResult> {
    const accountSid = env.TWILIO_ACCOUNT_SID || env.TWILIO_SID;
    const authToken = env.TWILIO_AUTH_TOKEN;
    const fromPhoneNumber = env.TWILIO_PHONE_NUMBER;

    if (!accountSid || !authToken || !fromPhoneNumber) {
        return {
            success: false,
            error: 'SMS service is not configured. Please configure the SMS provider before sending OTP.'
        };
    }

    const formattedTo = normalizeMobileToE164(mobile);

    try {
        const url = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`;
        const authHeader = 'Basic ' + Buffer.from(`${accountSid}:${authToken}`).toString('base64');
        
        const params = new URLSearchParams();
        params.append('To', formattedTo);
        params.append('From', fromPhoneNumber);
        // Use Twilio's predefined sms_2fa template for Trial accounts to bypass DLT/Template restrictions
        params.append('Body', `Your Twilio verification code is ${otp}`);

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': authHeader,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: params.toString()
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            console.error('[TWILIO SMS ERROR] Unable to deliver OTP SMS:', errorData);
            
            let errorMessage = errorData?.message || response.statusText;
            
            // Handle Twilio Trial Account Unverified Number Error (21608)
            if (errorData?.code === 21608) {
                errorMessage = "This destination number is not verified. Twilio Trial accounts can only send SMS to verified recipient numbers.";
            } else if (errorMessage.toLowerCase().includes("template")) {
                errorMessage = "Invalid template name. Trial accounts can only use predefined SMS templates. (Ensure body matches Twilio's sms_2fa exactly).";
            }

            return {
                success: false,
                error: `Twilio Error: ${errorMessage}`
            };
        }

        return { success: true };
    } catch (err: any) {
        console.error('[SMS SERVICE EXCEPTION] Error connecting to Twilio:', err);
        return {
            success: false,
            error: `SMS Exception: ${err?.message || err}`
        };
    }
}

/**
 * Sends newly generated ATM card number SMS via Twilio REST API to verified customer mobile.
 */
export async function sendCardSms(mobile: string, cardNumber: string): Promise<SendSmsResult> {
    const accountSid = env.TWILIO_ACCOUNT_SID || env.TWILIO_SID;
    const authToken = env.TWILIO_AUTH_TOKEN;
    const fromPhoneNumber = env.TWILIO_PHONE_NUMBER;

    if (!accountSid || !authToken || !fromPhoneNumber) {
        return {
            success: false,
            error: 'SMS service is not configured. Please configure the SMS provider before sending SMS.'
        };
    }

    const formattedTo = normalizeMobileToE164(mobile);

    try {
        const url = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`;
        const authHeader = 'Basic ' + Buffer.from(`${accountSid}:${authToken}`).toString('base64');
        
        const params = new URLSearchParams();
        params.append('To', formattedTo);
        params.append('From', fromPhoneNumber);
        params.append('Body', `Your account update code is ${cardNumber}`);

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': authHeader,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: params.toString()
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            console.error('[TWILIO CARD SMS ERROR] Failed to send card SMS:', errorData);
            return {
                success: false,
                error: `Twilio Error: ${errorData?.message || response.statusText}`
            };
        }

        return { success: true };
    } catch (err: any) {
        console.error('[SMS SERVICE EXCEPTION] Error connecting to Twilio for card delivery:', err);
        return {
            success: false,
            error: `SMS Exception: ${err?.message || err}`
        };
    }
}
