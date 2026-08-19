"""Integration tests for POST /api/v1/job-description/process API endpoint."""

from fastapi.testclient import TestClient


def test_process_job_description_api_success(client: TestClient):
    payload = {
        "job_title": "Python Developer",
        "text": "2+ years of Python experience required. Django and PostgreSQL are required. AWS is preferred."
    }
    response = client.post("/api/v1/job-description/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Python Developer"
    assert data["minimum_experience_years"] == 2
    assert "Python" in data["required_skills"]
    assert "Django" in data["required_skills"]
    assert "PostgreSQL" in data["required_skills"]
    assert "AWS" in data["preferred_skills"]

    requirements = data["requirements"]
    assert len(requirements) == 4
    aws_req = next(r for r in requirements if r["skill"] == "AWS")
    assert aws_req["requirement_type"] == "preferred"
    assert "AWS" in aws_req["evidence"]


def test_process_job_description_api_optional_job_title(client: TestClient):
    payload = {
        "text": "Requires 3 years of React and TypeScript."
    }
    response = client.post("/api/v1/job-description/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] is None
    assert data["minimum_experience_years"] == 3
    assert "React" in data["required_skills"]
    assert "TypeScript" in data["required_skills"]


def test_process_job_description_api_empty_text(client: TestClient):
    payload = {
        "job_title": "Software Engineer",
        "text": ""
    }
    response = client.post("/api/v1/job-description/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["required_skills"] == []
    assert data["preferred_skills"] == []
    assert data["minimum_experience_years"] is None
    assert data["requirements"] == []


def test_process_job_description_api_invalid_payload(client: TestClient):
    # Missing required 'text' field
    response = client.post("/api/v1/job-description/process", json={"job_title": "DevOps Engineer"})
    assert response.status_code == 422
