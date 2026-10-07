import nodemailer from 'nodemailer';
import { env } from '$env/dynamic/private';

export interface SecurityAlertEmailPayload {
    toEmail: string;
    ownerName: string;
    cardNumber: string;
    failureReason: string;
    timestamp: string;
    attemptedImageUrl?: string;
}

export interface CardDeliveryEmailPayload {
    toEmail: string;
    customerName: string;
    bankName: string;
    accountNumber: string;
    cardNumber: string;
}

export async function sendSecurityAlertEmail(payload: SecurityAlertEmailPayload): Promise<boolean> {
    const smtpHost = env.SMTP_HOST || 'smtp.gmail.com';
    const smtpPort = parseInt(env.SMTP_PORT || '587', 10);
    const smtpUser = env.SMTP_USER || '';
    const smtpPass = env.SMTP_PASSWORD || env.SMTP_PASS || '';

    console.log(`[SECURITY ALERT EMAIL] Preparing alert for Original Account Owner: ${payload.toEmail} (${payload.ownerName})`);
    console.log(`[SECURITY ALERT DETAILS] Card: ${payload.cardNumber} | Reason: ${payload.failureReason} | Time: ${payload.timestamp}`);

    if (!smtpUser || !smtpPass) {
        console.warn(`[SECURITY ALERT EMAIL WARNING] SMTP_USER or SMTP_PASSWORD not configured in .env. Email notification logged but not dispatched over network.`);
        return false;
    }

    try {
        const transporter = nodemailer.createTransport({
            host: smtpHost,
            port: smtpPort,
            secure: smtpPort === 465,
            auth: {
                user: smtpUser,
                pass: smtpPass
            }
        });

        const maskedCard = payload.cardNumber.length >= 4 
            ? 'XXXX-XXXX-' + payload.cardNumber.slice(-4) 
            : payload.cardNumber;

        const mailOptions = {
            from: `"SecureATM Fraud Control" <${smtpUser}>`,
            to: payload.toEmail,
            subject: `🚨 Security Alert: Unauthorized ATM Access Attempt on Account ${maskedCard}`,
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
                    <div style="background-color: #ef4444; color: white; padding: 16px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h2 style="margin: 0;">SECURITY ALERT</h2>
                        <p style="margin: 4px 0 0 0; font-size: 14px;">Unauthorized ATM Access Attempt Detected</p>
                    </div>
                    
                    <div style="padding: 24px; color: #1e293b; line-height: 1.6;">
                        <p>Dear <strong>${payload.ownerName}</strong>,</p>
                        
                        <p>An unsuccessful biometric face authentication attempt was detected on your ATM account. Access to your funds was <strong>REJECTED</strong> and your account remains secure.</p>
                        
                        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f8fafc; border-radius: 8px;">
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Card Number:</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-family: monospace;">${maskedCard}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Incident Time:</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">${payload.timestamp}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Failure Reason:</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #dc2626; font-weight: bold;">${payload.failureReason}</td>
                            </tr>
                        </table>

                        <p style="color: #475569; font-size: 14px;">If this attempt was not made by you, please contact Bank Customer Support immediately to lock your card or initiate an investigation.</p>
                    </div>

                    <div style="background-color: #f1f5f9; padding: 12px; text-align: center; font-size: 12px; color: #64748b; border-radius: 0 0 8px 8px;">
                        SecureATM Multi-Factor Biometric Surveillance System &copy; 2026
                    </div>
                </div>
            `
        };

        const info = await transporter.sendMail(mailOptions);
        console.log(`[SECURITY ALERT EMAIL SUCCESS] Email dispatched to ${payload.toEmail}. Message ID: ${info.messageId}`);
        return true;
    } catch (error) {
        console.error(`[SECURITY ALERT EMAIL ERROR] Failed to send email to ${payload.toEmail}:`, error);
        return false;
    }
}

export async function sendCardDeliveryEmail(payload: CardDeliveryEmailPayload): Promise<boolean> {
    const smtpHost = env.SMTP_HOST || 'smtp.gmail.com';
    const smtpPort = parseInt(env.SMTP_PORT || '587', 10);
    const smtpUser = env.SMTP_USER || '';
    const smtpPass = env.SMTP_PASSWORD || env.SMTP_PASS || '';

    const maskedAcc = payload.accountNumber.length >= 4 
        ? '********' + payload.accountNumber.slice(-4) 
        : payload.accountNumber;

    const maskedCard = 'XXXX XXXX XXXX ' + payload.cardNumber.slice(-4);

    console.log(`[CARD DELIVERY EMAIL] Sending card notification to ${payload.toEmail} (${payload.customerName})`);
    console.log(`[CARD DELIVERY DETAILS] Bank: ${payload.bankName} | Account: ${maskedAcc} | Card: ${payload.cardNumber}`);

    if (!smtpUser || !smtpPass) {
        console.warn(`[CARD DELIVERY EMAIL NOTICE] SMTP credentials not set in .env. Card notification logged securely.`);
        return false;
    }

    try {
        const transporter = nodemailer.createTransport({
            host: smtpHost,
            port: smtpPort,
            secure: smtpPort === 465,
            auth: { user: smtpUser, pass: smtpPass }
        });

        const mailOptions = {
            from: `"SecureATM Cards Team" <${smtpUser}>`,
            to: payload.toEmail,
            subject: `Your Secure ATM Card Registration — ${payload.bankName}`,
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
                    <div style="background-color: #2563eb; color: white; padding: 16px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h2 style="margin: 0;">Secure ATM Card Registration</h2>
                        <p style="margin: 4px 0 0 0; font-size: 14px;">Official Account Notification</p>
                    </div>
                    
                    <div style="padding: 24px; color: #1e293b; line-height: 1.6;">
                        <p>Dear <strong>${payload.customerName}</strong>,</p>
                        
                        <p>Your Secure ATM account has been successfully registered by Bank Administration.</p>
                        
                        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f8fafc; border-radius: 8px;">
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Customer Name:</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">${payload.customerName}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Bank Name:</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">${payload.bankName}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Account Number:</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-family: monospace;">${maskedAcc}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Generated ATM Card Number:</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-family: monospace; font-weight: bold; color: #2563eb;">${maskedCard}</td>
                            </tr>
                        </table>

                        <p style="color: #475569; font-size: 14px;">Your original account owner face has been securely linked to your profile for ATM biometric authentication. Please keep your card information secure.</p>
                    </div>

                    <div style="background-color: #f1f5f9; padding: 12px; text-align: center; font-size: 12px; color: #64748b; border-radius: 0 0 8px 8px;">
                        SecureATM Multi-Factor Biometric Banking System &copy; 2026
                    </div>
                </div>
            `
        };

        await transporter.sendMail(mailOptions);
        return true;
    } catch (err) {
        console.error(`[CARD DELIVERY EMAIL ERROR] Failed to send card delivery email:`, err);
        return false;
    }
}
