import os
import base64
from fastapi.testclient import TestClient
from fastapi_service.main import app

client = TestClient(app)

def get_sample_b64_image():
    img_path = os.path.join(os.path.dirname(__file__), "..", "..", "legacy", "myface.jpg")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

def test_check_liveness_sample():
    b64_img = get_sample_b64_image()
    if b64_img is None:
        pytest.skip("Test sample image legacy/myface.jpg not found")

    response = client.post("/api/v1/ml/check-liveness", json={"image_b64": b64_img})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "is_live" in data
    assert "liveness_score" in data
    assert data["decision"] in ["LIVE", "SPOOF", "UNCERTAIN"]
