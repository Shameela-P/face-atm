import cv2
import time
import numpy as np
from fastapi import HTTPException
from fastapi_service.config import settings
from fastapi_service.models.mtcnn_detector import MTCNNDetectorLoader
from fastapi_service.models.liveness_model import LivenessModelLoader
from fastapi_service.services.detection_service import decode_base64_image
from fastapi_service.schemas.biometric import LivenessResponse

def detect_mobile_photo_texture(face_img: np.ndarray) -> bool:
    """
    Algorithmic texture variance check. Low standard deviation indicates flat photo / display reflection.
    """
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    texture_std = np.std(gray)
    return texture_std < settings.TEXTURE_STD_THRESHOLD

def check_liveness_service(b64_string: str) -> LivenessResponse:
    start_time = time.time()
    img = decode_base64_image(b64_string)

    detector = MTCNNDetectorLoader.get_detector()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = detector.detect_faces(img_rgb)

    if len(results) == 0:
        raise HTTPException(status_code=400, detail={"code": "NO_FACE", "message": "No face detected for liveness check"})
    if len(results) > 1:
        raise HTTPException(status_code=400, detail={"code": "MULTIPLE_FACES", "message": "Multiple faces detected. Exactly one face required for liveness check"})

    x, y, w, h = results[0]['box']
    x, y = max(0, x), max(0, y)
    face_roi = img[y:y+h, x:x+w]

    if face_roi.size == 0 or face_roi.shape[0] < 10 or face_roi.shape[1] < 10:
        raise HTTPException(status_code=400, detail={"code": "LOW_FACE_CONFIDENCE", "message": "Extracted face region of interest is too small"})

    # Step A: Texture Analysis (Flag flat mobile photos with std < 12)
    if detect_mobile_photo_texture(face_roi):
        proc_time = round((time.time() - start_time) * 1000, 2)
        return LivenessResponse(
            success=True,
            is_live=False,
            liveness_score=0.10,
            decision="SPOOF",
            model_version="TextureAnalysis-StdDev+CNN",
            processing_time_ms=proc_time
        )

    # Step B: Liveness CNN Inference
    model = LivenessModelLoader.get_model()
    target_w, target_h = LivenessModelLoader.get_target_size()

    face_resized = cv2.resize(face_roi, (target_w, target_h))
    face_normalized = face_resized.astype("float32") / 255.0
    face_input = np.expand_dims(face_normalized, axis=0)

    predictions = model.predict(face_input, verbose=0)[0]
    
    # Class 0 = 'real' (live face), Class 1 = 'spoof'
    if len(predictions) >= 2:
        live_score = float(predictions[0])
    else:
        live_score = float(predictions[0])

    is_live = live_score >= settings.LIVENESS_THRESHOLD # Default 0.45

    # Determine decision with uncertainty band
    if live_score >= 0.45:
        decision = "LIVE"
    elif live_score < 0.30:
        decision = "SPOOF"
    else:
        decision = "UNCERTAIN" if is_live else "SPOOF"

    proc_time = round((time.time() - start_time) * 1000, 2)
    return LivenessResponse(
        success=True,
        is_live=is_live,
        liveness_score=round(live_score, 4),
        decision=decision,
        model_version="KerasLivenessCNN-64x64",
        processing_time_ms=proc_time
    )
