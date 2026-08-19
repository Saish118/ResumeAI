"""Integration tests for POST /api/v1/role/predict API endpoint."""

from fastapi.testclient import TestClient


def test_predict_role_api_success(client: TestClient):
    payload = {
        "text": "Experienced Systems Engineer proficient in Python, Linux, networking, and cloud security infrastructure."
    }
    response = client.post("/api/v1/role/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_role" in data
    assert "confidence" in data
    assert isinstance(data["predicted_role"], str)
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_role_api_empty_text(client: TestClient):
    payload = {"text": ""}
    response = client.post("/api/v1/role/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_role"] == "Unknown"
    assert data["confidence"] == 0.0


def test_predict_role_api_invalid_payload(client: TestClient):
    # Missing required 'text' field
    response = client.post("/api/v1/role/predict", json={})
    assert response.status_code == 422
