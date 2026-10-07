export interface SendSmsResult {
    success: boolean;
    error?: string;
}

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
    const accountSid = process.env.TWILIO_ACCOUNT_SID || process.env.TWILIO_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const fromPhoneNumber = process.env.TWILIO_PHONE_NUMBER;

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
        params.append('Body', `SecureATM verification code: ${otp}. This code expires in 5 minutes. Do not share this code.`);

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
            console.error('[TWILIO SMS ERROR] Unable to deliver OTP SMS.');
            return {
                success: false,
                error: errorData?.message || 'Unable to send OTP right now. Please try again later.'
            };
        }

        return { success: true };
    } catch (err: any) {
        console.error('[SMS SERVICE EXCEPTION] Error connecting to Twilio');
        return {
            success: false,
            error: 'Unable to send OTP right now. Please try again later.'
        };
    }
}

/**
 * Sends newly generated ATM card number SMS via Twilio REST API to verified customer mobile.
 */
export async function sendCardSms(mobile: string, cardNumber: string): Promise<SendSmsResult> {
    const accountSid = process.env.TWILIO_ACCOUNT_SID || process.env.TWILIO_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const fromPhoneNumber = process.env.TWILIO_PHONE_NUMBER;

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
        params.append('Body', `SecureATM: Your ATM card has been successfully generated. Card Number: ${cardNumber}. Please keep your card details secure.`);

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
            console.error('[TWILIO CARD SMS ERROR] Failed to send card SMS.');
            return {
                success: false,
                error: errorData?.message || 'Failed to deliver card notification SMS.'
            };
        }

        return { success: true };
    } catch (err: any) {
        console.error('[SMS SERVICE EXCEPTION] Error connecting to Twilio for card delivery');
        return {
            success: false,
            error: 'Failed to communicate with SMS provider for card delivery.'
        };
    }
}
