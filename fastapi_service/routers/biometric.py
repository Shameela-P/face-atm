from fastapi import APIRouter
from fastapi_service.schemas.biometric import (
    Base64ImageRequest,
    DetectionResponse,
    LivenessResponse,
    EmbeddingResponse,
    VerificationRequest,
    VerificationResponse,
    ActiveChallengeRequestContract
)
from fastapi_service.services.detection_service import detect_faces_service
from fastapi_service.services.liveness_service import check_liveness_service
from fastapi_service.services.embedding_service import generate_embedding_service
from fastapi_service.services.verification_service import verify_authentication_service

router = APIRouter(prefix="/api/v1/ml", tags=["Biometric ML Services"])

@router.post("/detect-face", response_model=DetectionResponse)
def detect_face(req: Base64ImageRequest):
    return detect_faces_service(req.image_b64)

@router.post("/check-liveness", response_model=LivenessResponse)
def check_liveness(req: Base64ImageRequest):
    return check_liveness_service(req.image_b64)

@router.post("/generate-embedding", response_model=EmbeddingResponse)
def generate_embedding(req: Base64ImageRequest):
    return generate_embedding_service(req.image_b64)

@router.post("/verify-authentication", response_model=VerificationResponse)
def verify_authentication(req: VerificationRequest):
    return verify_authentication_service(req)

@router.post("/check-active-liveness")
def check_active_liveness_contract(req: ActiveChallengeRequestContract):
    """
    API Contract documentation endpoint for multi-frame active liveness challenges.
    Will be populated with sequence optical flow / landmark trajectory checks in Phase 3.
    """
    return {
        "status": "contract_defined",
        "session_id": req.session_id,
        "received_frames_count": len(req.frames),
        "supported_challenges": ["BLINK", "TURN_LEFT", "TURN_RIGHT", "LOOK_UP", "LOOK_DOWN"],
        "message": "Active challenge multi-frame contract validated successfully."
    }
