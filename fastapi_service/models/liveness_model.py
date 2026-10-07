import os
import logging
import tensorflow as tf
from fastapi_service.config import settings

logger = logging.getLogger(__name__)

class LivenessModelLoader:
    _instance = None
    _model = None
    _input_shape = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_path = os.path.abspath(settings.LIVENESS_MODEL_PATH)
            logger.info(f"Loading Liveness Model from {model_path}...")
            if not os.path.exists(model_path):
                # Fallback to liveness.model if liveness_model.h5 is absent
                fallback_path = os.path.join(os.path.dirname(model_path), "liveness.model")
                if os.path.exists(fallback_path):
                    model_path = fallback_path

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Liveness model file not found at: {model_path}")

            try:
                cls._model = tf.keras.models.load_model(model_path, compile=False)
                cls._input_shape = cls._model.input_shape
                logger.info(f"Liveness Model loaded successfully! Verified Input Shape: {cls._input_shape}")
            except Exception as e:
                logger.error(f"Failed to load Liveness model: {e}")
                raise RuntimeError(f"Liveness model loading error: {e}")
        return cls._model

    @classmethod
    def get_target_size(cls) -> tuple:
        if cls._input_shape is None:
            cls.get_model()
        # Shape is (None, H, W, C)
        h = cls._input_shape[1] if cls._input_shape[1] is not None else 64
        w = cls._input_shape[2] if cls._input_shape[2] is not None else 64
        return (w, h)

    @classmethod
    def is_ready(cls) -> bool:
        return cls._model is not None
