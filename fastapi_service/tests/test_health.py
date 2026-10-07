import pytest
from fastapi.testclient import TestClient
from fastapi_service.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "face-biometric-service"
    assert "models" in data
    assert data["models"]["mtcnn"] is True
    assert data["models"]["facenet"] is True
    assert data["models"]["liveness"] is True
