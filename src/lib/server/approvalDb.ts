import { ref, get, set, update, child } from 'firebase/database';
import { firebaseRtdb } from './firebaseDb';
import crypto from 'crypto';

export interface ApprovalRequestRecord {
    id: string; // Token ID
    customerId: string;
    cardNumber: string;
    attemptedImageUrl: string;
    status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED' | 'CONSUMED';
    maxAmount?: number;
    otpHash?: string;
    otpExpiry?: string;
    otpAttempts?: number;
    createdAt: string;
}

export async function createApprovalRequest(params: {
    customerId: string;
    cardNumber: string;
    attemptedImageUrl: string;
}): Promise<string> {
    const tokenId = crypto.randomUUID();
    const createdAt = new Date().toISOString();
    
    const record: ApprovalRequestRecord = {
        id: tokenId,
        customerId: params.customerId,
        cardNumber: params.cardNumber,
        attemptedImageUrl: params.attemptedImageUrl,
        status: 'PENDING',
        createdAt
    };

    await set(ref(firebaseRtdb, `remoteApprovals/${tokenId}`), record);
    return tokenId;
}

export async function getApprovalRequest(tokenId: string): Promise<ApprovalRequestRecord | null> {
    const snapshot = await get(child(ref(firebaseRtdb), `remoteApprovals/${tokenId}`));
    if (snapshot.exists()) {
        return snapshot.val() as ApprovalRequestRecord;
    }
    return null;
}

export async function updateApprovalRequestStatus(tokenId: string, status: ApprovalRequestRecord['status'], maxAmount?: number): Promise<void> {
    const updates: any = { status };
    if (maxAmount !== undefined) {
        updates.maxAmount = maxAmount;
    }
    await update(ref(firebaseRtdb, `remoteApprovals/${tokenId}`), updates);
}

export async function storeApprovalOtp(tokenId: string, otpHash: string, expiryMs: number = 5 * 60 * 1000): Promise<void> {
    const otpExpiry = new Date(Date.now() + expiryMs).toISOString();
    await update(ref(firebaseRtdb, `remoteApprovals/${tokenId}`), {
        otpHash,
        otpExpiry,
        otpAttempts: 0
    });
}

export async function incrementApprovalOtpAttempts(tokenId: string, currentAttempts: number): Promise<void> {
    await update(ref(firebaseRtdb, `remoteApprovals/${tokenId}`), {
        otpAttempts: currentAttempts + 1
    });
}

export async function consumeApproval(tokenId: string): Promise<void> {
    await update(ref(firebaseRtdb, `remoteApprovals/${tokenId}`), {
        status: 'CONSUMED'
    });
}
