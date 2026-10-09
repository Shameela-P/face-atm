/**
 * Centralized ML Service Client for communicating with the Python FastAPI Microservice.
 * Reads ML_SERVICE_URL from process.env with default fallback to http://localhost:8000.
 */

import { env } from '$env/dynamic/private';

export function getMlServiceUrl(): string {
    return env.ML_SERVICE_URL || process.env.ML_SERVICE_URL || 'http://127.0.0.1:8000';
}

export interface MlHealthResponse {
    status: string;
    service: string;
    models?: {
        mtcnn: boolean;
        facenet: boolean;
        liveness: boolean;
    };
}

export interface MlEmbeddingResponse {
    success: boolean;
    embedding: number[];
    face_count: number;
    aligned: boolean;
    message?: string;
}

export interface MlVerifyResponse {
    match: boolean;
    liveness_passed: boolean;
    distance: number;
    similarity: number;
    threshold_distance: number;
    threshold_similarity: number;
    message: string;
}

/**
 * Checks health of FastAPI ML microservice at /health
 */
export async function checkMlServiceHealth(): Promise<{ online: boolean; data?: MlHealthResponse; error?: string }> {
    const baseUrl = getMlServiceUrl();
    try {
        const res = await fetch(`${baseUrl}/health`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            signal: AbortSignal.timeout(3000)
        });

        if (res.ok) {
            const data = await res.json() as MlHealthResponse;
            return { online: true, data };
        }
        return { online: false, error: `ML Service returned status ${res.status}` };
    } catch (err: any) {
        return { 
            online: false, 
            error: `Face recognition service is currently unavailable at ${baseUrl}. Please start the ML service and try again.` 
        };
    }
}

/**
 * Generates 128-d FaceNet embedding for Original Owner Face registration
 */
export async function generateFaceEmbedding(imageB64: string): Promise<{ success: boolean; embedding?: number[]; error?: string }> {
    const baseUrl = getMlServiceUrl();
    try {
        const res = await fetch(`${baseUrl}/api/v1/ml/generate-embedding`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_b64: imageB64 }),
            signal: AbortSignal.timeout(15000)
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            const msg = errData.detail?.message || errData.detail || 'Face quality check failed.';
            return { success: false, error: `Biometric Processing Error: ${msg}` };
        }

        const data = await res.json() as MlEmbeddingResponse;
        if (!data.success || !data.embedding || data.embedding.length === 0) {
            return { success: false, error: 'Could not extract valid face embedding for Original Owner.' };
        }

        return { success: true, embedding: data.embedding };
    } catch (err: any) {
        console.error(`[ML Service Connection Failure] POST ${baseUrl}/api/v1/ml/generate-embedding:`, err?.message || err);
        return { 
            success: false, 
            error: `Face recognition service error: ${err?.message || 'Connection failed'}` 
        };
    }
}

/**
 * Verifies live camera frame against target account owner embedding
 */
export async function verifyFaceAuthentication(params: {
    imageB64: string;
    targetEmbedding: number[];
}): Promise<{ success: boolean; data?: MlVerifyResponse; errorCode?: string; error?: string }> {
    const baseUrl = getMlServiceUrl();
    try {
        const res = await fetch(`${baseUrl}/api/v1/ml/verify-authentication`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_b64: params.imageB64,
                target_embedding: params.targetEmbedding
            }),
            signal: AbortSignal.timeout(15000)
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            const code = errData.detail?.code || 'ML_ERROR';
            const msg = errData.detail?.message || 'Biometric verification processing error.';
            return { success: false, errorCode: code, error: msg };
        }

        const data = await res.json() as MlVerifyResponse;
        return { success: true, data };
    } catch (err: any) {
        console.error(`[ML Service Connection Failure] POST ${baseUrl}/api/v1/ml/verify-authentication:`, err?.message || err);
        return { 
            success: false, 
            errorCode: 'SERVICE_OFFLINE', 
            error: `Face recognition service error: ${err?.message || 'Connection failed'}` 
        };
    }
}
