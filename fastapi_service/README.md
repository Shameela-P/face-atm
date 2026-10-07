# FastAPI Biometric & Machine Learning Service

Stateless Python FastAPI microservice responsible for facial detection, MTCNN 5-point alignment, Liveness CNN anti-spoofing verification, and FaceNet embedding calculation.

---

## 1. Directory Structure

```
fastapi_service/
├── main.py                    # FastAPI application instance & middleware
├── config.py                  # Environment & threshold settings
├── requirements.txt           # Python dependencies
├── .env.example               # Configuration template
├── models/                    # Model loader singletons
│   ├── mtcnn_detector.py      # MTCNN face detector loader
│   ├── facenet_model.py       # Keras FaceNet loader (128-d / 512-d dynamic verification)
│   ├── liveness_model.py      # Keras Liveness CNN loader (64x64)
│   └── face_alignment.py      # 5-point landmark facial alignment
├── services/                  # Core ML business logic
│   ├── detection_service.py   # Base64 validation & MTCNN face detection
│   ├── liveness_service.py    # Texture analysis + Liveness CNN inference
│   ├── embedding_service.py   # FaceNet vector extraction & L2 normalization
│   └── verification_service.py# Identity verification against target vector
├── schemas/                   # Pydantic request/response data contracts
│   └── biometric.py
├── routers/                   # FastAPI route controllers
│   ├── health.py              # Health check endpoint
│   └── biometric.py           # ML REST endpoints
└── tests/                     # Test suite
    ├── test_health.py
    ├── test_detection.py
    ├── test_liveness.py
    └── test_embedding.py
```

---

## 2. Requirements & Setup

### Prerequisites
- Python 3.7+
- TensorFlow 2.11.0
- OpenCV 4.7.0+
- MTCNN 0.1.0+

### Installation & Launch

```bash
# Navigate to fastapi_service directory
cd fastapi_service

# Install dependencies
pip install -r requirements.txt

# Start FastAPI service
python main.py
```

The service runs on `http://localhost:8000`. OpenAPI documentation is accessible at `http://localhost:8000/docs`.

---

## 3. Verified Model Specifications

- **MTCNN Detector:** `mtcnn` package. Detects facial bounding boxes and 5 keypoints (`left_eye`, `right_eye`, `nose`, `mouth_left`, `mouth_right`).
- **FaceNet Model (`legacy/facenet_keras.h5`):**
  - Input Shape: `(None, 160, 160, 3)`
  - Output Vector Dimension: **128** (Verified dynamically at runtime).
  - Normalization: L2 Normalized vector float array.
- **Liveness Model (`legacy/liveness_model.h5`):**
  - Input Shape: `(None, 64, 64, 3)`
  - Output Shape: `(None, 2)` (Binary classification score: Class 1 = Live Face).

---

## 4. API Endpoint Specifications

### `GET /health`
Returns service health and model readiness status.

### `POST /api/v1/ml/detect-face`
Detects faces in a Base64 encoded image frame using MTCNN.

### `POST /api/v1/ml/check-liveness`
Runs texture variance check and Liveness CNN inference over face ROI.

### `POST /api/v1/ml/generate-embedding`
Aligns face, extracts 128-d FaceNet embedding vector, and returns L2 normalized float array.

### `POST /api/v1/ml/verify-authentication`
Compares live camera frame against the target account owner's stored vector using Euclidean distance and Cosine similarity.

---

## 5. Security & Privacy Guarantees

- **No Global User Search:** Verification requests take a single target embedding belonging to the account owner.
- **Stateless Operation:** Raw images are decoded in memory and destroyed immediately after inference. No biometric images are saved to disk.
- **No Secret Leakage:** Exception handlers prevent raw stack traces or internal filesystem paths from being returned to clients.
