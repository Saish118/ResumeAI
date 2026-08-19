"""Integration tests for POST /api/v1/resume/skills API endpoint."""

from fastapi.testclient import TestClient


def test_extract_skills_api_success(client: TestClient):
    payload = {
        "text": "Built applications using Python, React.js and PostgreSQL."
    }
    response = client.post("/api/v1/resume/skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == ["Python", "React", "PostgreSQL"]

    # Verify structured extractions list
    extracted = data["extracted_skills"]
    assert len(extracted) == 3
    assert extracted[0]["skill"] == "Python"
    assert extracted[0]["category"] == "Programming Languages"
    assert extracted[1]["skill"] == "React"
    assert extracted[1]["category"] == "Web Development"
    assert extracted[2]["skill"] == "PostgreSQL"
    assert extracted[2]["category"] == "Databases"


def test_extract_skills_api_empty_text(client: TestClient):
    payload = {"text": ""}
    response = client.post("/api/v1/resume/skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == []
    assert data["extracted_skills"] == []


def test_extract_skills_api_no_skills_matched(client: TestClient):
    payload = {"text": "Non-technical background in creative writing and music production."}
    response = client.post("/api/v1/resume/skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == []


def test_extract_skills_api_invalid_payload(client: TestClient):
    # Missing required 'text' field
    response = client.post("/api/v1/resume/skills", json={})
    assert response.status_code == 422
