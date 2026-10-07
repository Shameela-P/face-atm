from fastapi import APIRouter
try:
    from fastapi_service.models.mtcnn_detector import MTCNNDetectorLoader
    from fastapi_service.models.facenet_model import FaceNetModelLoader
    from fastapi_service.models.liveness_model import LivenessModelLoader
except ImportError:
    from models.mtcnn_detector import MTCNNDetectorLoader
    from models.facenet_model import FaceNetModelLoader
    from models.liveness_model import LivenessModelLoader

router = APIRouter(tags=["Health"])

@router.get("/")
@router.get("/health")
def health_check():
    mtcnn_ok = MTCNNDetectorLoader.is_ready()
    facenet_ok = FaceNetModelLoader.is_ready()
    liveness_ok = LivenessModelLoader.is_ready()

    return {
        "status": "ok",
        "service": "face-ml",
        "models": {
            "mtcnn": mtcnn_ok,
            "facenet": facenet_ok,
            "liveness": liveness_ok
        }
    }
