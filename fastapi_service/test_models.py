import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from fastapi_service.config import settings
    from fastapi_service.models.mtcnn_detector import MTCNNDetectorLoader
    from fastapi_service.models.facenet_model import FaceNetModelLoader
    from fastapi_service.models.liveness_model import LivenessModelLoader
    
    print("Testing ML Loaders...")
    print("Loading MTCNN...")
    MTCNNDetectorLoader.get_detector()
    print("MTCNN: OK")
    print("Loading Liveness...")
    LivenessModelLoader.get_model()
    print("Liveness: OK")
    print("Loading FaceNet...")
    FaceNetModelLoader.get_model()
    print("FaceNet: OK")
except Exception as e:
    import traceback
    traceback.print_exc()
