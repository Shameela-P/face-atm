import { fail, redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { sendSecurityAlertEmail, sendMismatchApprovalEmail } from '$lib/server/email';
import { uploadImageToFirebaseStorage } from '$lib/server/firebase';
import { createApprovalRequest } from '$lib/server/approvalDb';
import { getCustomerByIdFromFirebase, getFaceRecordByCustomerIdFromFirebase, recordSecurityIncidentInFirebase, recordFaceVerificationInFirebase, getSecurityIncidentsFromFirebase, createComplaintInFirebase } from '$lib/server/firebaseDb';
import { verifyFaceAuthentication } from '$lib/server/mlService';

export const load: PageServerLoad = async ({ cookies }) => {
    const uidStr = cookies.get('atm_session_uid');
    const cardStr = cookies.get('atm_session_card');
    
    if (!uidStr || !cardStr) {
        throw redirect(303, '/atm');
    }

    const customer = await getCustomerByIdFromFirebase(uidStr);
    if (!customer) {
        throw redirect(303, '/atm');
    }

    // Retrieve Original Account Owner's Registered Embedding from Firebase Realtime Database
    const faceRecord = await getFaceRecordByCustomerIdFromFirebase(uidStr);
    
    let hasRegisteredEmbedding = false;
    let registeredEmbedding: number[] = [];

    if (faceRecord && faceRecord.embedding) {
        try {
            registeredEmbedding = JSON.parse(faceRecord.embedding);
            hasRegisteredEmbedding = Array.isArray(registeredEmbedding) && registeredEmbedding.length > 0;
        } catch (e) {
            console.error("Error parsing embedding JSON from Firebase:", e);
        }
    }

    return {
        uid: uidStr,
        card: cardStr,
        ownerName: customer.name,
        ownerEmail: customer.email,
        hasRegisteredEmbedding,
        registeredEmbedding
    };
};

export const actions: Actions = {
    verifyFace: async ({ request, cookies }) => {
        const uidStr = cookies.get('atm_session_uid');
        const cardStr = cookies.get('atm_session_card');

        if (!uidStr || !cardStr) {
            return fail(401, { error: 'ATM session expired. Please re-enter your card.' });
        }

        const data = await request.formData();
        const photoDataUrl = data.get('image')?.toString();

        if (!photoDataUrl) {
            return fail(400, { error: 'No camera frame captured. Please position your face inside the frame.' });
        }

        const customer = await getCustomerByIdFromFirebase(uidStr);
        if (!customer) {
            return fail(404, { error: 'Account owner not found in Firebase Realtime Database.' });
        }

        const faceRecord = await getFaceRecordByCustomerIdFromFirebase(uidStr);
        if (!faceRecord || !faceRecord.embedding) {
            return fail(400, { error: `Original Account Owner (${customer.name}) has no registered face embedding in Firebase. Please ask Admin to register the owner's face first.` });
        }

        let registeredEmbedding: number[] = [];
        try {
            registeredEmbedding = JSON.parse(faceRecord.embedding);
        } catch (e) {
            return fail(500, { error: 'Failed to parse registered biometric template vector.' });
        }

        // Call FastAPI ML Service helper to verify LIVE face against ONLY THAT CARD OWNER'S REGISTERED EMBEDDING
        const mlRes = await verifyFaceAuthentication({
            imageB64: photoDataUrl,
            targetEmbedding: registeredEmbedding
        });

        if (!mlRes.success) {
            if (mlRes.errorCode === 'NO_FACE') {
                return fail(400, { error: 'No face detected in camera frame. Please position your face in the camera.' });
            }
            if (mlRes.errorCode === 'MULTIPLE_FACES') {
                return fail(400, { error: 'Multiple faces detected! Only one person must be in front of the ATM.' });
            }
            return fail(400, { error: mlRes.error || 'Face recognition service is currently unavailable. Please start the ML service and try again.' });
        }

        const mlResult = mlRes.data!;

        // Check verification outcome
        if (mlResult.match && mlResult.liveness_passed) {
            // Record successful face verification event in Firebase Realtime Database
            await recordFaceVerificationInFirebase({
                customerId: uidStr,
                cardNumber: cardStr,
                result: 'MATCH'
            });

            // SUCCESSFUL AUTHENTICATION MATCH FOR THIS CARD OWNER
            cookies.set('atm_authenticated', 'true', {
                path: '/',
                httpOnly: true,
                sameSite: 'lax',
                maxAge: 60 * 15 // 15 minutes session
            });

            return { success: true, message: 'Identity Verified Successfully' };
        } else {
            // WRONG PERSON / MISMATCH OR SPOOF ATTEMPT
            const failureReason = !mlResult.liveness_passed 
                ? 'Liveness Check Failed (Spoof / Photo Attempt Detected)' 
                : `Face Mismatch (Distance: ${mlResult.distance}, Cosine Sim: ${mlResult.similarity})`;

            console.warn(`[SECURITY WRONG FACE DETECTED] Card: ${cardStr} | Owner: ${customer.name} (${customer.email}) | Reason: ${failureReason}`);

            // 1. Upload attempted person image to Firebase Storage
            const timestampStr = Date.now().toString();
            const incidentStoragePath = `face-images/security-incidents/${uidStr}/${timestampStr}/attempted-face.jpg`;
            let attemptedImageUrl = photoDataUrl;
            try {
                attemptedImageUrl = await uploadImageToFirebaseStorage(photoDataUrl, incidentStoragePath);
            } catch (fbErr) {
                console.warn("[Firebase Storage Incident Upload Warning]:", fbErr);
            }

            // 2. Log incident in securityIncidents table in Firebase Realtime Database
            await recordSecurityIncidentInFirebase({
                customerId: uidStr,
                cardNumber: cardStr,
                attemptedImageUrl,
                incidentType: !mlResult.liveness_passed ? 'SPOOF_DETECTED' : 'FACE_MISMATCH',
                status: 'UNAUTHORIZED_ATTEMPT'
            });

            // Detect repeated attempts (e.g. >= 3 in last 24h)
            const allIncidents = await getSecurityIncidentsFromFirebase();
            const recentIncidents = allIncidents.filter(inc => 
                inc.customerId === uidStr && 
                new Date(inc.timestamp).getTime() > Date.now() - 24 * 60 * 60 * 1000
            );

            if (recentIncidents.length >= 3) {
                await createComplaintInFirebase({
                    customerId: uidStr,
                    customerName: customer.fullName || customer.name || 'Customer',
                    email: customer.email || '',
                    category: 'Fraud & Security',
                    subject: 'Multiple Unauthorized ATM Access Attempts',
                    description: `Detected ${recentIncidents.length} unauthorized access attempts in the last 24 hours using card ${cardStr}.`,
                    priority: 'URGENT'
                });
            }

            // Create Approval Request
            const tokenId = await createApprovalRequest({
                customerId: uidStr,
                cardNumber: cardStr,
                attemptedImageUrl
            });

            const baseUrl = request.headers.get('origin') || 'http://localhost:5173';
            const absoluteImageUrl = attemptedImageUrl.startsWith('/') 
                ? `${baseUrl}${attemptedImageUrl}` 
                : attemptedImageUrl;

            // Dispatch Security Alert Email & Approval Link to ORIGINAL ACCOUNT OWNER
            await sendMismatchApprovalEmail({
                toEmail: customer.email || '',
                ownerName: customer.fullName || customer.name || 'Customer',
                cardNumber: cardStr,
                attemptTime: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
                approvalToken: tokenId,
                baseUrl: baseUrl,
                attemptedImageUrl: absoluteImageUrl || photoDataUrl,
                attemptedImageBase64: photoDataUrl
            });

            throw redirect(303, `/atm/await-approval/${tokenId}`);
        }
    }
} satisfies Actions;
