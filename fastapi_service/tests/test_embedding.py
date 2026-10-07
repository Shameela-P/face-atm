import os
import base64
import pytest
from fastapi.testclient import TestClient
from fastapi_service.main import app

client = TestClient(app)

def get_sample_b64_image():
    img_path = os.path.join(os.path.dirname(__file__), "..", "..", "legacy", "myface.jpg")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

def test_generate_embedding_dimension():
    b64_img = get_sample_b64_image()
    if b64_img is None:
        pytest.skip("Test sample image legacy/myface.jpg not found")

    response = client.post("/api/v1/ml/generate-embedding", json={"image_b64": b64_img})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["normalized"] is True
    # Verify exact loaded model dimension (128 for facenet_keras.h5)
    assert data["embedding_dimension"] == len(data["embedding"])
    assert data["embedding_dimension"] == 128

def test_verify_authentication_mismatch_dimension():
    b64_img = get_sample_b64_image()
    if b64_img is None:
        pytest.skip("Test sample image legacy/myface.jpg not found")

    # Send 512-dim dummy vector to a 128-dim model to test dimension rejection
    dummy_vector = [0.1] * 512
    response = client.post("/api/v1/ml/verify-authentication", json={
        "image_b64": b64_img,
        "target_embedding": dummy_vector
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TARGET_EMBEDDING"
