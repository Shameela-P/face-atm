from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class Base64ImageRequest(BaseModel):
    image_b64: str = Field(..., description="Base64 encoded JPEG or PNG image string")

class FaceBox(BaseModel):
    box: List[int] = Field(..., description="Bounding box [x, y, width, height]")
    confidence: float = Field(..., description="Detection confidence score")

class DetectionResponse(BaseModel):
    success: bool
    face_count: int
    faces: List[FaceBox]
    message: Optional[str] = None
    processing_time_ms: float

class EmbeddingResponse(BaseModel):
    success: bool
    embedding_dimension: int
    normalized: bool
    embedding: List[float]
    processing_time_ms: float

class LivenessResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    success: bool
    is_live: bool
    liveness_score: float
    decision: str  # LIVE, SPOOF, UNCERTAIN
    model_version: str
    processing_time_ms: float

class VerificationRequest(BaseModel):
    image_b64: str = Field(..., description="Base64 encoded live camera frame")
    target_embedding: List[float] = Field(..., description="Vector embedding of the account owner")

class VerificationResponse(BaseModel):
    success: bool
    match: bool
    liveness_passed: bool
    liveness_score: float
    distance: float
    similarity: float
    threshold: float
    threshold_status: str
    decision: str  # AUTHENTICATED, REJECTED_SPOOF, REJECTED_MISMATCH, REJECTED_MULTIPLE_FACES, REJECTED_NO_FACE
    processing_time_ms: float

class ActiveChallengeStep(BaseModel):
    challenge_type: str  # BLINK, TURN_LEFT, TURN_RIGHT, LOOK_UP, LOOK_DOWN
    frame_b64: str

class ActiveChallengeRequestContract(BaseModel):
    session_id: str
    frames: List[ActiveChallengeStep]
