import logging
from mtcnn import MTCNN

logger = logging.getLogger(__name__)

class MTCNNDetectorLoader:
    _instance = None
    _detector = None

    @classmethod
    def get_detector(cls):
        if cls._detector is None:
            logger.info("Initializing MTCNN Face Detector...")
            try:
                cls._detector = MTCNN()
                logger.info("MTCNN Face Detector initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize MTCNN: {e}")
                raise RuntimeError(f"MTCNN initialization failed: {e}")
        return cls._detector

    @classmethod
    def is_ready(cls) -> bool:
        return cls._detector is not None
