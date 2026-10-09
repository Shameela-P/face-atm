import os
import logging
import tensorflow as tf
from fastapi_service.config import settings

logger = logging.getLogger(__name__)

@tf.keras.utils.register_keras_serializable()
class ScaleSumLayer(tf.keras.layers.Layer):
    def __init__(self, scale, **kwargs):
        super().__init__(**kwargs)
        self.scale = scale

    def call(self, inputs):
        return inputs[0] + inputs[1] * self.scale

    def get_config(self):
        config = super().get_config()
        config.update({'scale': self.scale})
        return config

class FaceNetModelLoader:
    _instance = None
    _model = None
    _output_dim = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_path = os.path.abspath(settings.FACENET_MODEL_PATH)
            logger.info(f"Loading FaceNet Keras Model from {model_path}...")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"FaceNet model file not found at: {model_path}")
            try:
                cls._model = tf.keras.models.load_model(
                    model_path, 
                    compile=False, 
                    custom_objects={'ScaleSumLayer': ScaleSumLayer}
                )
                output_shape = cls._model.output_shape
                cls._output_dim = output_shape[1] if isinstance(output_shape, tuple) else output_shape[0][1]
                logger.info(f"FaceNet Model loaded successfully! Verified Output Dimension: {cls._output_dim}")
            except Exception as e:
                logger.error(f"Failed to load FaceNet model: {e}")
                raise RuntimeError(f"FaceNet model loading error: {e}")
        return cls._model

    @classmethod
    def get_output_dimension(cls) -> int:
        if cls._output_dim is None:
            cls.get_model()
        return cls._output_dim

    @classmethod
    def is_ready(cls) -> bool:
        return cls._model is not None
