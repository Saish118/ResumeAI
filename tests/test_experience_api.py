"""Integration tests for POST /api/v1/resume/experience API endpoint."""

from fastapi.testclient import TestClient


def test_extract_experience_api_success(client: TestClient):
    payload = {
        "text": "Senior Backend Developer with 5 years of experience in Python, FastAPI, and Docker."
    }
    response = client.post("/api/v1/resume/experience", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_experience_years"] == 5.0
    assert "evidence" in data
    assert data["confidence"] in ("high", "medium")


def test_extract_experience_api_no_experience(client: TestClient):
    payload = {
        "text": "Student looking for entry level opportunities. Skills: Python, HTML."
    }
    response = client.post("/api/v1/resume/experience", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_experience_years"] is None
    assert data["confidence"] == "low"


def test_extract_experience_api_missing_payload(client: TestClient):
    response = client.post("/api/v1/resume/experience", json={})
    assert response.status_code == 422
