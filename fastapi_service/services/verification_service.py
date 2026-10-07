import time
import numpy as np
from fastapi import HTTPException
from fastapi_service.config import settings
from fastapi_service.models.facenet_model import FaceNetModelLoader
from fastapi_service.services.liveness_service import check_liveness_service
from fastapi_service.services.embedding_service import generate_embedding_service
from fastapi_service.schemas.biometric import VerificationRequest, VerificationResponse

def calculate_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

def verify_authentication_service(req: VerificationRequest) -> VerificationResponse:
    start_time = time.time()
    expected_dim = FaceNetModelLoader.get_output_dimension()

    # Validate target embedding dimension
    if len(req.target_embedding) != expected_dim:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_TARGET_EMBEDDING",
                "message": f"Target embedding dimension {len(req.target_embedding)} does not match model dimension {expected_dim}"
            }
        )

    # Step A: Check Liveness
    try:
        liveness_res = check_liveness_service(req.image_b64)
    except HTTPException as e:
        code = e.detail.get("code") if isinstance(e.detail, dict) else "LIVENESS_FAILED"
        proc_time = round((time.time() - start_time) * 1000, 2)
        decision = "REJECTED_NO_FACE" if code == "NO_FACE" else "REJECTED_MULTIPLE_FACES" if code == "MULTIPLE_FACES" else "REJECTED_SPOOF"
        return VerificationResponse(
            success=False,
            match=False,
            liveness_passed=False,
            liveness_score=0.0,
            distance=999.0,
            similarity=0.0,
            threshold=settings.FACE_DISTANCE_THRESHOLD,
            threshold_status="EXPERIMENTAL",
            decision=decision,
            processing_time_ms=proc_time
        )

    if not liveness_res.is_live:
        proc_time = round((time.time() - start_time) * 1000, 2)
        return VerificationResponse(
            success=True,
            match=False,
            liveness_passed=False,
            liveness_score=liveness_res.liveness_score,
            distance=999.0,
            similarity=0.0,
            threshold=settings.FACE_DISTANCE_THRESHOLD,
            threshold_status="EXPERIMENTAL",
            decision="REJECTED_SPOOF",
            processing_time_ms=proc_time
        )

    # Step B: Generate Embedding for incoming frame
    emb_res = generate_embedding_service(req.image_b64)
    live_vector = np.array(emb_res.embedding, dtype=np.float32)
    target_vector = np.array(req.target_embedding, dtype=np.float32)

    # Calculate distance & similarity
    euclidean_distance = float(np.linalg.norm(live_vector - target_vector))
    cosine_sim = calculate_cosine_similarity(live_vector, target_vector)

    # Compare against threshold
    is_match = euclidean_distance <= settings.FACE_DISTANCE_THRESHOLD
    decision = "AUTHENTICATED" if is_match else "REJECTED_MISMATCH"

    proc_time = round((time.time() - start_time) * 1000, 2)
    return VerificationResponse(
        success=True,
        match=is_match,
        liveness_passed=True,
        liveness_score=liveness_res.liveness_score,
        distance=round(euclidean_distance, 4),
        similarity=round(cosine_sim, 4),
        threshold=settings.FACE_DISTANCE_THRESHOLD,
        threshold_status="EXPERIMENTAL",
        decision=decision,
        processing_time_ms=proc_time
    )
