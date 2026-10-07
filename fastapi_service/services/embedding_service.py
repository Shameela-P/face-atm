import cv2
import time
import numpy as np
from fastapi import HTTPException
from fastapi_service.models.mtcnn_detector import MTCNNDetectorLoader
from fastapi_service.models.face_alignment import align_face
from fastapi_service.models.facenet_model import FaceNetModelLoader
from fastapi_service.services.detection_service import decode_base64_image
from fastapi_service.schemas.biometric import EmbeddingResponse

def generate_embedding_service(b64_string: str) -> EmbeddingResponse:
    start_time = time.time()
    img = decode_base64_image(b64_string)

    detector = MTCNNDetectorLoader.get_detector()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = detector.detect_faces(img_rgb)

    if len(results) == 0:
        raise HTTPException(status_code=400, detail={"code": "NO_FACE", "message": "No face detected for embedding generation"})
    if len(results) > 1:
        raise HTTPException(status_code=400, detail={"code": "MULTIPLE_FACES", "message": "Multiple faces detected. Exactly one face required"})

    face_info = results[0]
    x, y, w, h = face_info['box']
    x, y = max(0, x), max(0, y)

    # Crop Face ROI
    face_roi_rgb = img_rgb[y:y+h, x:x+w]
    if face_roi_rgb.size == 0 or face_roi_rgb.shape[0] < 10 or face_roi_rgb.shape[1] < 10:
        raise HTTPException(status_code=400, detail={"code": "LOW_FACE_CONFIDENCE", "message": "Extracted face region of interest is invalid"})

    keypoints = face_info.get('keypoints', {})

    # Face alignment & resize to 160x160 for FaceNet
    aligned_face_rgb = align_face(face_roi_rgb, keypoints, desired_face_width=160, desired_face_height=160)
    aligned_face_rgb = cv2.resize(aligned_face_rgb, (160, 160))

    # FaceNet Preprocessing
    face_norm = aligned_face_rgb.astype("float32") / 255.0
    face_tensor = np.expand_dims(face_norm, axis=0)

    # FaceNet Inference
    facenet = FaceNetModelLoader.get_model()
    raw_embedding = facenet.predict(face_tensor, verbose=0)[0]

    # L2 Normalization
    norm = np.linalg.norm(raw_embedding)
    if norm > 0:
        normalized_embedding = (raw_embedding / norm).tolist()
    else:
        normalized_embedding = raw_embedding.tolist()

    dimension = FaceNetModelLoader.get_output_dimension()
    proc_time = round((time.time() - start_time) * 1000, 2)

    return EmbeddingResponse(
        success=True,
        embedding_dimension=dimension,
        normalized=True,
        embedding=[round(float(v), 6) for v in normalized_embedding],
        processing_time_ms=proc_time
    )
