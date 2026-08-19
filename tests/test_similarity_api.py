"""Integration tests for POST /api/v1/similarity API endpoint."""

from fastapi.testclient import TestClient
from app.services.similarity_service import MODEL_NAME


def test_similarity_api_success(client: TestClient):
    payload = {
        "text_a": "Built REST APIs using FastAPI and Python.",
        "text_b": "Developed backend services and REST APIs."
    }
    response = client.post("/api/v1/similarity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "similarity_score" in data
    assert data["model_name"] == MODEL_NAME
    assert 0.0 <= data["similarity_score"] <= 1.0
    assert data["similarity_score"] > 0.5


def test_similarity_api_empty_text(client: TestClient):
    payload = {
        "text_a": "",
        "text_b": "Some text string"
    }
    response = client.post("/api/v1/similarity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["similarity_score"] == 0.0


def test_similarity_api_invalid_payload(client: TestClient):
    # Missing required 'text_b' field
    response = client.post("/api/v1/similarity", json={"text_a": "Only text_a provided"})
    assert response.status_code == 422
