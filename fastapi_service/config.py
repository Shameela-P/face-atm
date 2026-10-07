import os

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    FACENET_MODEL_PATH: str = os.getenv(
        "FACENET_MODEL_PATH",
        os.path.join(BASE_DIR, "legacy", "facenet_keras.h5")
    )
    LIVENESS_MODEL_PATH: str = os.getenv(
        "LIVENESS_MODEL_PATH",
        os.path.join(BASE_DIR, "legacy", "liveness_model.h5")
    )

    # Experimental thresholds (Configurable, non-production hardcode)
    LIVENESS_THRESHOLD: float = float(os.getenv("LIVENESS_THRESHOLD", "0.45"))
    TEXTURE_STD_THRESHOLD: float = float(os.getenv("TEXTURE_STD_THRESHOLD", "12.0"))
    FACE_DISTANCE_THRESHOLD: float = float(os.getenv("FACE_DISTANCE_THRESHOLD", "1.15"))
    FACE_COSINE_SIMILARITY_THRESHOLD: float = float(os.getenv("FACE_COSINE_SIMILARITY_THRESHOLD", "0.40"))

    # Security constraints
    MAX_PAYLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    MIN_IMAGE_DIMENSION: int = 64
    MAX_IMAGE_DIMENSION: int = 4096

settings = Settings()
