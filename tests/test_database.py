"""Unit and integration tests for PostgreSQL/SQLAlchemy database layer and history endpoints."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base, get_db, init_db
from app.db.models import ResumeAnalysis, JobAnalysis, MatchAnalysis


@pytest.fixture
def test_db_session(db_isolation: Session) -> Session:
    """Provides an isolated database session for testing."""
    return db_isolation


@pytest.fixture
def db_client(client: TestClient) -> TestClient:
    """Provides a FastAPI TestClient configured with test database isolation."""
    return client


def test_database_connection_and_table_creation(test_db_session: Session):
    """Verifies that database connection and table creation succeed."""
    assert test_db_session is not None
    # Verify tables can be queried
    res_count = test_db_session.query(ResumeAnalysis).count()
    job_count = test_db_session.query(JobAnalysis).count()
    match_count = test_db_session.query(MatchAnalysis).count()
    assert res_count == 0
    assert job_count == 0
    assert match_count == 0


def test_saving_and_querying_resume_analysis(test_db_session: Session):
    """Verifies saving and retrieving a ResumeAnalysis record."""
    rec = ResumeAnalysis(
        filename="test_resume.pdf",
        file_type="pdf",
        character_count=1200,
        page_count=2,
        extracted_text="John Doe - Senior Software Engineer with Python skills",
        predicted_role="Software Engineer",
        role_model_score=0.92,
        candidate_experience_years=4.5,
    )
    test_db_session.add(rec)
    test_db_session.commit()
    test_db_session.refresh(rec)

    assert rec.id is not None
    fetched = test_db_session.query(ResumeAnalysis).filter_by(id=rec.id).first()
    assert fetched is not None
    assert fetched.filename == "test_resume.pdf"
    assert fetched.predicted_role == "Software Engineer"
    assert fetched.candidate_experience_years == 4.5


def test_saving_and_querying_job_analysis(test_db_session: Session):
    """Verifies saving and retrieving a JobAnalysis record."""
    rec = JobAnalysis(
        job_title="Senior Python Backend Engineer",
        job_description="Seeking a Python engineer with 3+ years experience in FastAPI and PostgreSQL.",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Docker", "AWS"],
        minimum_experience_years=3,
    )
    test_db_session.add(rec)
    test_db_session.commit()
    test_db_session.refresh(rec)

    assert rec.id is not None
    fetched = test_db_session.query(JobAnalysis).filter_by(id=rec.id).first()
    assert fetched is not None
    assert fetched.job_title == "Senior Python Backend Engineer"
    assert fetched.required_skills == ["Python", "FastAPI", "PostgreSQL"]


def test_saving_match_analysis_with_foreign_keys(test_db_session: Session):
    """Verifies saving MatchAnalysis linked via foreign keys to ResumeAnalysis and JobAnalysis."""
    resume_rec = ResumeAnalysis(
        filename="alice.pdf",
        file_type="pdf",
        character_count=500,
        extracted_text="Alice Smith - Python Developer",
        predicted_role="Software Engineer",
    )
    job_rec = JobAnalysis(
        job_title="Python Developer",
        job_description="Need Python developer",
        required_skills=["Python"],
    )
    test_db_session.add_all([resume_rec, job_rec])
    test_db_session.commit()

    match_rec = MatchAnalysis(
        resume_analysis_id=resume_rec.id,
        job_analysis_id=job_rec.id,
        overall_score=85.5,
        matched_required_skills=["Python"],
        missing_required_skills=[],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
        experience_status="matched",
        candidate_experience_years=4.0,
        required_experience_years=3,
        semantic_evidence_matches=[{"skill": "Python", "score": 0.88}],
        summary="Candidate meets all requirements.",
    )
    test_db_session.add(match_rec)
    test_db_session.commit()
    test_db_session.refresh(match_rec)

    assert match_rec.id is not None
    assert match_rec.resume_analysis_id == resume_rec.id
    assert match_rec.job_analysis_id == job_rec.id
    assert match_rec.resume_analysis.filename == "alice.pdf"
    assert match_rec.job_analysis.job_title == "Python Developer"


def test_history_api_endpoints(db_client: TestClient, test_db_session: Session):
    """Tests GET /api/v1/history/resumes, /jobs, /matches, and /matches/{id}."""
    # Seed data
    r = ResumeAnalysis(
        filename="bob.docx", file_type="docx", character_count=400, extracted_text="Bob Data Analyst"
    )
    j = JobAnalysis(
        job_title="Data Analyst", job_description="Data analysis role", required_skills=["SQL"]
    )
    test_db_session.add_all([r, j])
    test_db_session.commit()

    m = MatchAnalysis(
        resume_analysis_id=r.id,
        job_analysis_id=j.id,
        overall_score=90.0,
        matched_required_skills=["SQL"],
        missing_required_skills=[],
        experience_status="matched",
        summary="Strong fit",
    )
    test_db_session.add(m)
    test_db_session.commit()

    # Test GET /history/resumes
    res_resp = db_client.get("/api/v1/history/resumes")
    assert res_resp.status_code == 200
    res_data = res_resp.json()
    assert len(res_data) == 1
    assert res_data[0]["filename"] == "bob.docx"

    # Test GET /history/jobs
    job_resp = db_client.get("/api/v1/history/jobs")
    assert job_resp.status_code == 200
    job_data = job_resp.json()
    assert len(job_data) == 1
    assert job_data[0]["job_title"] == "Data Analyst"

    # Test GET /history/matches
    match_resp = db_client.get("/api/v1/history/matches")
    assert match_resp.status_code == 200
    match_data = match_resp.json()
    assert len(match_data) == 1
    assert match_data[0]["overall_score"] == 90.0

    # Test GET /history/matches/{id}
    detail_resp = db_client.get(f"/api/v1/history/matches/{m.id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == m.id
    assert detail_data["resume_analysis"]["filename"] == "bob.docx"
    assert detail_data["job_analysis"]["job_title"] == "Data Analyst"


def test_history_match_detail_not_found(db_client: TestClient):
    """Tests 404 response for nonexistent match ID."""
    resp = db_client.get("/api/v1/history/matches/99999")
    assert resp.status_code == 404
    assert "was not found" in resp.json()["detail"]


def test_invalid_database_url_handling():
    """Verifies handling of invalid/unreachable database URL."""
    invalid_engine = create_engine("postgresql+psycopg://invalid_user:invalid_pass@localhost:9999/nonexistent_db")
    with pytest.raises(Exception):
        invalid_engine.connect()
