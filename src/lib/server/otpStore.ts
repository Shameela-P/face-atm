import crypto from 'crypto';

interface OtpRecord {
    identifier: string;
    otpHash: string;
    createdAt: number;
    expiresAt: number;
    attempts: number;
    verified: boolean;
    sendTimestamps: number[];
    verifyTimestamps: number[];
}

export const verifiedEmails = new Set<string>();

const OTP_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes validity
const MAX_VERIFICATION_ATTEMPTS = 30; // Maximum 30 attempts per OTP session
const SEND_WINDOW_MS = 10 * 60 * 1000; // 10 minutes window
const MAX_SENDS_PER_WINDOW = 3; // Max 3 OTP sends per 10 minutes
const MIN_SEND_INTERVAL_MS = 60 * 1000; // Min 60s between sends
const VERIFY_WINDOW_MS = 60 * 1000; // 1 minute window
const MAX_VERIFY_PER_WINDOW = 10; // Max 10 verification requests per minute

const SECRET_SALT = 'SecureATM_OTP_Salt_2026_x89f';

// Server-side in-memory OTP store
const otpMap = new Map<string, OtpRecord>();

function normalizeKey(identifier: string): string {
    return identifier.trim().toLowerCase();
}

function hashOtp(otp: string): string {
    return crypto.createHash('sha256').update(otp + SECRET_SALT).digest('hex');
}

export function canSendOtp(identifier: string): { allowed: boolean; error?: string; status?: number } {
    const key = normalizeKey(identifier);
    const now = Date.now();
    const record = otpMap.get(key);

    if (record) {
        const recentSends = record.sendTimestamps.filter(t => now - t < SEND_WINDOW_MS);
        if (recentSends.length >= MAX_SENDS_PER_WINDOW) {
            return {
                allowed: false,
                status: 429,
                error: 'Too many OTP requests. Please wait before requesting another OTP.'
            };
        }

        const lastSend = recentSends[recentSends.length - 1];
        if (lastSend && now - lastSend < MIN_SEND_INTERVAL_MS) {
            return {
                allowed: false,
                status: 429,
                error: 'Too many OTP requests. Please wait before requesting another OTP.'
            };
        }
    }

    return { allowed: true };
}

export function storeOtp(identifier: string, otp: string): void {
    const key = normalizeKey(identifier);
    const now = Date.now();
    const expiresAt = now + OTP_EXPIRY_MS;
    const otpHash = hashOtp(otp);

    const existingRecord = otpMap.get(key);
    const recentSends = existingRecord
        ? existingRecord.sendTimestamps.filter(t => now - t < SEND_WINDOW_MS)
        : [];
    recentSends.push(now);

    otpMap.set(key, {
        identifier: key,
        otpHash,
        createdAt: now,
        expiresAt,
        attempts: 0,
        verified: false,
        sendTimestamps: recentSends,
        verifyTimestamps: existingRecord ? existingRecord.verifyTimestamps : []
    });
}

export function verifyOtp(identifier: string, enteredOtp: string): { success: boolean; error?: string; status?: number } {
    const key = normalizeKey(identifier);
    const now = Date.now();
    const record = otpMap.get(key);

    if (!record || !record.otpHash) {
        return { success: false, status: 400, error: 'No OTP requested for this email address or session expired.' };
    }

    // 1. Rate limiting for verify requests (Max 10 requests per minute per session)
    const recentVerifies = record.verifyTimestamps.filter(t => now - t < VERIFY_WINDOW_MS);
    if (recentVerifies.length >= MAX_VERIFY_PER_WINDOW) {
        return { success: false, status: 429, error: 'Too many verification attempts. Please wait and try again.' };
    }
    recentVerifies.push(now);
    record.verifyTimestamps = recentVerifies;

    // 2. Expiry check
    if (now > record.expiresAt) {
        otpMap.delete(key);
        return { success: false, status: 400, error: 'OTP expired. Please request a new OTP.' };
    }

    // 3. Maximum 30 attempts check
    if (record.attempts >= MAX_VERIFICATION_ATTEMPTS) {
        otpMap.delete(key);
        return { success: false, status: 400, error: 'Maximum OTP verification attempts exceeded. Please request a new OTP.' };
    }

    record.attempts += 1;

    // 4. Hash verification
    const inputHash = hashOtp(enteredOtp);
    if (record.otpHash !== inputHash) {
        if (record.attempts >= MAX_VERIFICATION_ATTEMPTS) {
            otpMap.delete(key);
            return { success: false, status: 400, error: 'Maximum OTP verification attempts exceeded. Please request a new OTP.' };
        }
        return { success: false, status: 400, error: 'Invalid OTP. Please enter the correct OTP.' };
    }

    // 5. Success - mark verified and IMMEDIATELY invalidate OTP hash so it cannot be reused
    record.verified = true;
    record.otpHash = ''; // Single-use invalidation
    otpMap.set(key, record);
    return { success: true };
}

export function isOtpVerified(identifier: string): boolean {
    const key = normalizeKey(identifier);
    const record = otpMap.get(key);
    return Boolean(record && record.verified && Date.now() <= record.expiresAt);
}

export function clearOtp(identifier: string): void {
    const key = normalizeKey(identifier);
    otpMap.delete(key);
}
