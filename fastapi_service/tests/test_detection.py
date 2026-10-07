import os
import base64
import cv2
import numpy as np
from fastapi.testclient import TestClient
from fastapi_service.main import app

client = TestClient(app)

def get_sample_b64_image():
    # Use legacy image if available
    img_path = os.path.join(os.path.dirname(__file__), "..", "..", "legacy", "myface.jpg")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    # Generate synthetic face-like image if file is absent
    synthetic = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(synthetic, (150, 150), 80, (200, 200, 200), -1)
    _, buffer = cv2.imencode(".jpg", synthetic)
    return base64.b64encode(buffer).decode("utf-8")

def test_detect_face_valid():
    b64_img = get_sample_b64_image()
    response = client.post("/api/v1/ml/detect-face", json={"image_b64": b64_img})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "face_count" in data
    assert isinstance(data["faces"], list)

def test_detect_face_invalid_b64():
    response = client.post("/api/v1/ml/detect-face", json={"image_b64": "invalid_base64_string"})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "UNSUPPORTED_IMAGE"
