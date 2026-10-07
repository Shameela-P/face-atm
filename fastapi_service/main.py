import sys
import os

# Add parent directory and current directory to sys.path to allow execution from root or fastapi_service/
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    from fastapi_service.config import settings
    from fastapi_service.models.mtcnn_detector import MTCNNDetectorLoader
    from fastapi_service.models.facenet_model import FaceNetModelLoader
    from fastapi_service.models.liveness_model import LivenessModelLoader
    from fastapi_service.routers import health, biometric
except ImportError:
    from config import settings
    from models.mtcnn_detector import MTCNNDetectorLoader
    from models.facenet_model import FaceNetModelLoader
    from models.liveness_model import LivenessModelLoader
    from routers import health, biometric

# Configure Safe Logging
logging.basicConfig(
    level=logging.INFO if settings.LOG_LEVEL.lower() == "info" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fastapi_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ML Models at Startup...")
    try:
        MTCNNDetectorLoader.get_detector()
        LivenessModelLoader.get_model()
        FaceNetModelLoader.get_model()
        logger.info("All ML Models successfully loaded and ready for inference!")
    except Exception as e:
        logger.error(f"Error initializing ML models during startup: {e}")
    yield
    logger.info("Shutting down FastAPI ML Service...")

app = FastAPI(
    title="Secure ATM Biometric ML Microservice",
    description="Isolated FastAPI microservice for MTCNN face detection, Liveness CNN anti-spoofing, and FaceNet embedding calculation.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for SvelteKit Localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ML_ERROR",
            "message": "An internal processing error occurred within the ML service."
        }
    )

# Performance Logging Middleware
@app.middleware("http")
async def log_request_performance(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    proc_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"Request: {request.method} {request.url.path} | Status: {response.status_code} | Duration: {proc_time}ms")
    return response

# Include Routers
app.include_router(health.router)
app.include_router(biometric.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
