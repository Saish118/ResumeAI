"""Unit tests for JobProcessor service."""

# pyrefly: ignore [missing-import]
import pytest
from app.schemas.job import JobProcessRequest
from app.services.job_processor import JobProcessor


@pytest.fixture
def processor() -> JobProcessor:
    return JobProcessor()


def test_required_skill_detection(processor: JobProcessor):
    req = JobProcessRequest(
        job_title="Backend Engineer",
        text="Python and PostgreSQL experience is required for this role."
    )
    res = processor.process_job_description(req)
    assert res.job_title == "Backend Engineer"
    assert "Python" in res.required_skills
    assert "PostgreSQL" in res.required_skills
    assert res.preferred_skills == []


def test_preferred_skill_detection(processor: JobProcessor):
    req = JobProcessRequest(
        job_title="Frontend Developer",
        text="React experience is required. Knowledge of Docker is preferred."
    )
    res = processor.process_job_description(req)
    assert "React" in res.required_skills
    assert "Docker" in res.preferred_skills


def test_reuse_of_alias_normalization(processor: JobProcessor):
    req = JobProcessRequest(
        text="Must have experience with postgres, sklearn, and reactjs. AWS is nice to have."
    )
    res = processor.process_job_description(req)
    # Check canonical normalization reuse
    assert "PostgreSQL" in res.required_skills
    assert "scikit-learn" in res.required_skills
    assert "React" in res.required_skills
    assert "AWS" in res.preferred_skills


def test_required_preferred_distinction(processor: JobProcessor):
    req = JobProcessRequest(
        text="Minimum 3 years of Python required. Django is essential. Knowledge of Redis and GCP is a bonus."
    )
    res = processor.process_job_description(req)
    assert "Python" in res.required_skills
    assert "Django" in res.required_skills
    assert "Redis" in res.preferred_skills
    assert "GCP" in res.preferred_skills


def test_minimum_experience_extraction(processor: JobProcessor):
    # Pattern: 2+ years
    res1 = processor.process_job_description(JobProcessRequest(text="2+ years of Python required."))
    assert res1.minimum_experience_years == 2

    # Pattern: 3-5 years
    res2 = processor.process_job_description(JobProcessRequest(text="Requires 3-5 years of software engineering experience."))
    assert res2.minimum_experience_years == 3

    # Pattern: minimum 4 years
    res3 = processor.process_job_description(JobProcessRequest(text="Minimum 4 years of experience with Linux."))
    assert res3.minimum_experience_years == 4

    # Pattern: at least 5 years
    res4 = processor.process_job_description(JobProcessRequest(text="At least 5 years of experience in data engineering."))
    assert res4.minimum_experience_years == 5


def test_no_skill_jd(processor: JobProcessor):
    req = JobProcessRequest(
        job_title="Community Manager",
        text="Looking for an energetic team player to host weekly events and coordinate newsletter updates."
    )
    res = processor.process_job_description(req)
    assert res.required_skills == []
    assert res.preferred_skills == []
    assert res.requirements == []
    assert res.minimum_experience_years is None


def test_empty_input(processor: JobProcessor):
    res_empty = processor.process_job_description(JobProcessRequest(text=""))
    assert res_empty.required_skills == []
    assert res_empty.preferred_skills == []
    assert res_empty.requirements == []
    assert res_empty.minimum_experience_years is None


def test_evidence_generation(processor: JobProcessor):
    req = JobProcessRequest(
        text="Strong experience in PyTorch is required for building deep learning models."
    )
    res = processor.process_job_description(req)
    assert len(res.requirements) >= 1
    pytorch_req = next(r for r in res.requirements if r.skill == "PyTorch")
    assert pytorch_req.requirement_type == "required"
    assert "PyTorch" in pytorch_req.evidence


def test_multiple_required_and_preferred_skills(processor: JobProcessor):
    req = JobProcessRequest(
        job_title="Full Stack Engineer",
        text="Requires 4+ years. Must have Python, FastAPI, and PostgreSQL. Docker and Kubernetes are preferred. GraphQL is nice to have."
    )
    res = processor.process_job_description(req)
    assert res.job_title == "Full Stack Engineer"
    assert res.minimum_experience_years == 4
    assert set(res.required_skills) == {"Python", "FastAPI", "PostgreSQL"}
    assert set(res.preferred_skills) == {"Docker", "Kubernetes", "GraphQL"}


def test_validate_jd_title_only(processor: JobProcessor):
    text1 = "Job Title: Software Developer"
    res1 = processor.process_job_description(JobProcessRequest(text=text1))
    valid1, reason1 = processor.validate_job_description(text1, res1)
    assert valid1 is False
    assert "Insufficient job description" in reason1

    text2 = "Software Engineer"
    res2 = processor.process_job_description(JobProcessRequest(text=text2))
    valid2, reason2 = processor.validate_job_description(text2, res2)
    assert valid2 is False
    assert "Insufficient job description" in reason2


def test_validate_jd_whitespace_only(processor: JobProcessor):
    text = "   \n\t  "
    valid, reason = processor.validate_job_description(text)
    assert valid is False
    assert "Insufficient job description" in reason


def test_validate_jd_title_and_boilerplate(processor: JobProcessor):
    text = "Job Title: Software Developer. We are hiring! Apply now. Great company to work for."
    res = processor.process_job_description(JobProcessRequest(text=text))
    valid, reason = processor.validate_job_description(text, res)
    assert valid is False
    assert "Insufficient job description" in reason


def test_validate_jd_one_required_skill(processor: JobProcessor):
    text = "Looking for a developer with Python."
    res = processor.process_job_description(JobProcessRequest(text=text))
    valid, reason = processor.validate_job_description(text, res)
    assert valid is True


def test_validate_jd_experience_requirement(processor: JobProcessor):
    text = "Requires 3 years of experience in software development."
    res = processor.process_job_description(JobProcessRequest(text=text))
    valid, reason = processor.validate_job_description(text, res)
    assert valid is True


def test_validate_jd_responsibilities_no_skills(processor: JobProcessor):
    text = "Responsibilities include designing REST APIs, writing unit tests, and conducting code reviews."
    res = processor.process_job_description(JobProcessRequest(text=text))
    valid, reason = processor.validate_job_description(text, res)
    assert valid is True


def test_validate_jd_preferred_skills(processor: JobProcessor):
    text = "Nice to have: Docker."
    res = processor.process_job_description(JobProcessRequest(text=text))
    valid, reason = processor.validate_job_description(text, res)
    assert valid is True

