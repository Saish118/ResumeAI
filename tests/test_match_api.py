"""Integration tests for POST /api/v1/match API endpoint."""

from fastapi.testclient import TestClient


def test_match_api_success(client: TestClient):
    payload = {
        "resume": {
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "extracted_skills": [
                {
                    "skill": "Python",
                    "matched_alias": "Python",
                    "category": "Programming Languages",
                    "evidence": "5 years of Python development experience."
                }
            ],
            "candidate_experience_years": 5
        },
        "job": {
            "job_title": "Senior Python Backend Engineer",
            "required_skills": ["Python", "PostgreSQL"],
            "preferred_skills": ["Docker"],
            "minimum_experience_years": 3,
            "requirements": [
                {
                    "skill": "Python",
                    "requirement_type": "required",
                    "evidence": "Minimum 3 years of Python backend engineering."
                }
            ]
        }
    }

    response = client.post("/api/v1/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert 0.0 <= data["overall_score"] <= 100.0
    assert data["matched_required_skills"] == ["Python", "PostgreSQL"]
    assert data["missing_required_skills"] == []
    assert data["missing_preferred_skills"] == ["Docker"]
    assert data["experience_assessment"]["status"] == "matched"
    assert data["experience_assessment"]["meets_requirement"] is True
    assert "summary" in data


def test_match_api_malformed_payload(client: TestClient):
    # Missing required 'job' object
    payload = {
        "resume": {
            "skills": ["Python"]
        }
    }
    response = client.post("/api/v1/match", json=payload)
    assert response.status_code == 422


def test_match_api_empty_skills_and_missing_experience(client: TestClient):
    payload = {
        "resume": {
            "skills": [],
            "extracted_skills": [],
            "candidate_experience_years": None
        },
        "job": {
            "job_title": "Junior Developer",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "minimum_experience_years": 2,
            "requirements": []
        }
    }
    response = client.post("/api/v1/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["missing_required_skills"] == ["Python"]
    assert data["experience_assessment"]["status"] == "unknown"
    assert 0.0 <= data["overall_score"] <= 100.0
