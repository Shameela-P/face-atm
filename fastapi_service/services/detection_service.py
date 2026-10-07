import base64
import cv2
import time
import numpy as np
from fastapi import HTTPException
from fastapi_service.config import settings
from fastapi_service.models.mtcnn_detector import MTCNNDetectorLoader
from fastapi_service.schemas.biometric import DetectionResponse, FaceBox

def decode_base64_image(b64_string: str) -> np.ndarray:
    """
    Decodes and validates a Base64 encoded image string.
    Checks payload size, format, and dimension constraints.
    """
    if not b64_string:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "Image payload is empty"})

    # Strip data URL prefix if present
    if "," in b64_string:
        header, encoded = b64_string.split(",", 1)
    else:
        encoded = b64_string

    # Payload size check
    if len(encoded) > settings.MAX_PAYLOAD_SIZE_BYTES * 1.35: # Base64 overhead ratio
        raise HTTPException(status_code=413, detail={"code": "PAYLOAD_TOO_LARGE", "message": "Image payload exceeds maximum limit of 10MB"})

    try:
        raw_bytes = base64.b64decode(encoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "UNSUPPORTED_IMAGE", "message": f"Base64 decoding failed: {str(e)}"})

    # Convert bytes to OpenCV Mat
    nparr = np.frombuffer(raw_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None or img.size == 0:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "Could not decode valid image pixels"})

    h, w = img.shape[:2]
    if h < settings.MIN_IMAGE_DIMENSION or w < settings.MIN_IMAGE_DIMENSION:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": f"Image dimension {w}x{h} below minimum threshold {settings.MIN_IMAGE_DIMENSION}x{settings.MIN_IMAGE_DIMENSION}"})

    if h > settings.MAX_IMAGE_DIMENSION or w > settings.MAX_IMAGE_DIMENSION:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": f"Image dimension {w}x{h} exceeds maximum threshold {settings.MAX_IMAGE_DIMENSION}x{settings.MAX_IMAGE_DIMENSION}"})

    return img

def detect_faces_service(b64_string: str) -> DetectionResponse:
    start_time = time.time()
    img = decode_base64_image(b64_string)

    detector = MTCNNDetectorLoader.get_detector()
    # MTCNN expects RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = detector.detect_faces(img_rgb)

    face_boxes = []
    for res in results:
        x, y, w, h = res['box']
        confidence = float(res['confidence'])
        # Ensure bounding box points remain within image bounds
        x = max(0, x)
        y = max(0, y)
        face_boxes.append(FaceBox(box=[x, y, w, h], confidence=confidence))

    proc_time = round((time.time() - start_time) * 1000, 2)
    face_count = len(face_boxes)

    msg = "Exactly one face detected" if face_count == 1 else f"{face_count} faces detected"
    return DetectionResponse(
        success=True,
        face_count=face_count,
        faces=face_boxes,
        message=msg,
        processing_time_ms=proc_time
    )
