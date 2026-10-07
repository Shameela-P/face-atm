import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getMlServiceUrl } from '$lib/server/mlService';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const body = await request.json();
        const imageB64 = body.imageB64 || body.image_b64;

        if (!imageB64) {
            return json({ success: false, error: 'Face frame image is required.' }, { status: 400 });
        }

        const baseUrl = getMlServiceUrl();

        // 1. Run Liveness Detection & Face Count check on FastAPI microservice
        const livenessRes = await fetch(`${baseUrl}/api/v1/ml/check-liveness`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_b64: imageB64 }),
            signal: AbortSignal.timeout(60000)
        });

        if (!livenessRes.ok) {
            const errData = await livenessRes.json().catch(() => ({}));
            const code = errData.detail?.code || errData.code;

            if (code === 'NO_FACE') {
                return json({ 
                    success: false, 
                    error: 'Face not detected. Please position the customer inside the frame.' 
                }, { status: 400 });
            }

            if (code === 'MULTIPLE_FACES') {
                return json({ 
                    success: false, 
                    error: 'Only the customer should be visible.' 
                }, { status: 400 });
            }

            if (code === 'LOW_FACE_CONFIDENCE') {
                return json({ 
                    success: false, 
                    error: 'Move closer to the camera.' 
                }, { status: 400 });
            }

            return json({ 
                success: false, 
                error: errData.detail?.message || 'Unable to verify that this is a live person. Please look directly at the camera and try again.' 
            }, { status: 400 });
        }

        const livenessData = await livenessRes.json();

        // 2. Enforce strict liveness decision checks
        if (livenessData.decision === 'SPOOF' || !livenessData.is_live) {
            return json({ 
                success: false, 
                error: 'Live person could not be verified. Please use the real account owner.' 
            }, { status: 400 });
        }

        if (livenessData.decision === 'UNCERTAIN') {
            return json({ 
                success: false, 
                error: 'Unable to verify that this is a live person. Please look directly at the camera and try again.' 
            }, { status: 400 });
        }

        if (livenessData.decision !== 'LIVE') {
            return json({ 
                success: false, 
                error: 'Live person could not be verified. Please use the real account owner.' 
            }, { status: 400 });
        }

        // 3. Test FaceNet embedding generation to guarantee face quality
        const embeddingRes = await fetch(`${baseUrl}/api/v1/ml/generate-embedding`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_b64: imageB64 }),
            signal: AbortSignal.timeout(60000)
        });

        if (!embeddingRes.ok) {
            return json({ 
                success: false, 
                error: 'Biometric face quality check failed. Please position face clearly and retry.' 
            }, { status: 400 });
        }

        const embeddingData = await embeddingRes.json();
        if (!embeddingData.success || !embeddingData.embedding || embeddingData.embedding.length === 0) {
            return json({ 
                success: false, 
                error: 'Failed to extract face embedding. Please try again.' 
            }, { status: 400 });
        }

        return json({
            success: true,
            message: 'Live customer verified & face captured successfully ✓'
        });
    } catch (err: any) {
        console.error('[Face Validation Error]:', err?.message || err);
        return json({ 
            success: false, 
            error: `Face recognition service error: ${err?.message || 'Connection failed'}`
        }, { status: 500 });
    }
};
