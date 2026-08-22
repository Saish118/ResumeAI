"""Regression test suite for preferred-vs-required skill classification logic."""

# pyrefly: ignore [missing-import]
import pytest
from app.schemas.job import JobProcessRequest
from app.schemas.match import MatchRequest, ResumeDataInput, JobDataInput
from app.services.job_processor import job_processor
from app.services.matching_engine import matching_engine

MIXED_DOMAIN_QA_JD = """
Senior Software Engineer / Data Engineer

Required Skills:
- Python
- FastAPI
- React
- PostgreSQL
- Git
- AWS
- Kubernetes
- Terraform

Preferred Skills:
- Docker
- Tableau
- Figma

Minimum experience:
4 years
"""

MIXED_DOMAIN_CANDIDATE_RESUME = """
SUMMARY
Senior Software Engineer with 4 years of experience in Python, FastAPI, React, PostgreSQL, and Git.
Worked extensively with Docker containerization for local development.

SKILLS
Python, FastAPI, React, PostgreSQL, Git, Docker

EXPERIENCE
• Developed backend microservices with Python and FastAPI.
• Built frontend web interfaces using React.
• Managed relational databases with PostgreSQL.
• Used Git for version control and Docker for local environment containerization.
"""

QA1_STRONG_JD = """
Python Backend Developer

Required Skills:
- Python
- FastAPI
- PostgreSQL

Preferred Skills:
- AWS
- Docker

Minimum Experience: 3 years
"""

QA2_DEVOPS_JD = """
DevOps Lead Engineer

Required:
- Docker
- Kubernetes
- Terraform
- AWS
- Linux
- Git
- GCP
- Azure
- Python

Minimum experience:
5 years
"""

QA4_DESIGN_JD = """
Senior Graphic Designer

Required:
- Adobe Photoshop
- Adobe Illustrator
- Figma
- After Effects
- Premiere Pro
- UI/UX Design
- Brand Identity
- Typography
- Motion Graphics

Minimum experience:
5 years.
"""


def test_mixed_domain_qa_exact_skill_classification():
    res = job_processor.process_job_description(JobProcessRequest(text=MIXED_DOMAIN_QA_JD, job_title="Senior Software Engineer"))
    
    # 1. Preferred Docker stays preferred
    assert "Docker" in res.preferred_skills
    assert "Docker" not in res.required_skills

    # 2. Preferred Tableau stays preferred
    assert "Tableau" in res.preferred_skills
    assert "Tableau" not in res.required_skills

    # 3. Preferred Figma stays preferred
    assert "Figma" in res.preferred_skills
    assert "Figma" not in res.required_skills

    # 4. Required AWS stays required
    assert "AWS" in res.required_skills
    assert "AWS" not in res.preferred_skills

    # 5. Required Kubernetes stays required
    assert "Kubernetes" in res.required_skills
    assert "Kubernetes" not in res.preferred_skills

    # 6. Required Terraform stays required
    assert "Terraform" in res.required_skills
    assert "Terraform" not in res.preferred_skills

    # 7. Required/preferred classification survives taxonomy normalization
    docker_detail = next(r for r in res.requirements if r.skill == "Docker")
    assert docker_detail.requirement_type == "preferred"
    assert docker_detail.recognized_by_taxonomy is True

    aws_detail = next(r for r in res.requirements if r.skill == "AWS")
    assert aws_detail.requirement_type == "required"
    assert aws_detail.recognized_by_taxonomy is True

    assert len(res.required_skills) == 8
    assert set(res.required_skills) == {"Python", "FastAPI", "React", "PostgreSQL", "Git", "AWS", "Kubernetes", "Terraform"}
    assert set(res.preferred_skills) == {"Docker", "Tableau", "Figma"}


def test_scoring_separates_required_and_preferred_skills():
    processed_job = job_processor.process_job_description(JobProcessRequest(text=MIXED_DOMAIN_QA_JD))
    match_req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "React", "PostgreSQL", "Git", "Docker"],
            raw_text=MIXED_DOMAIN_CANDIDATE_RESUME,
            candidate_experience_years=4.0,
        ),
        job=JobDataInput(
            job_title=processed_job.job_title,
            required_skills=processed_job.required_skills,
            preferred_skills=processed_job.preferred_skills,
            minimum_experience_years=processed_job.minimum_experience_years,
            requirements=processed_job.requirements,
        )
    )
    result = matching_engine.match(match_req)

    # 8. Required skill score excludes preferred skills (matched 5 of 8 required skills)
    assert set(result.matched_required_skills) == {"Python", "FastAPI", "React", "PostgreSQL", "Git"}
    assert set(result.missing_required_skills) == {"AWS", "Kubernetes", "Terraform"}
    assert "Docker" not in result.matched_required_skills

    # 9. Preferred skill score excludes required skills (matched 1 of 3 preferred skills)
    assert result.matched_preferred_skills == ["Docker"]
    assert set(result.missing_preferred_skills) == {"Tableau", "Figma"}


def test_qa1_strong_jd_regression():
    res = job_processor.process_job_description(JobProcessRequest(text=QA1_STRONG_JD, job_title="Python Backend Developer"))
    assert set(res.required_skills) == {"Python", "FastAPI", "PostgreSQL"}
    assert set(res.preferred_skills) == {"AWS", "Docker"}

    match_req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"],
            raw_text="Senior Python Backend Developer with 4 years experience in Python, FastAPI, PostgreSQL, AWS, Docker.",
            candidate_experience_years=4.0,
        ),
        job=JobDataInput(
            job_title=res.job_title,
            required_skills=res.required_skills,
            preferred_skills=res.preferred_skills,
            minimum_experience_years=res.minimum_experience_years,
            requirements=res.requirements,
        )
    )

    result = matching_engine.match(match_req)
    assert result.overall_score >= 90.0
    assert set(result.matched_required_skills) == {"Python", "FastAPI", "PostgreSQL"}
    assert set(result.matched_preferred_skills) == {"AWS", "Docker"}


def test_qa2_devops_jd_regression():
    res = job_processor.process_job_description(JobProcessRequest(text=QA2_DEVOPS_JD, job_title="DevOps Lead Engineer"))
    assert len(res.required_skills) == 9

    match_req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "Git", "AWS"],
            candidate_experience_years=3.0,
        ),
        job=JobDataInput(
            job_title=res.job_title,
            required_skills=res.required_skills,
            preferred_skills=res.preferred_skills,
            minimum_experience_years=res.minimum_experience_years,
            requirements=res.requirements,
        )
    )
    result = matching_engine.match(match_req)
    assert result.overall_score < 50.0
    assert set(result.matched_required_skills) == {"Python", "Git", "AWS"}


def test_qa4_non_taxonomy_requirements_regression():
    res = job_processor.process_job_description(JobProcessRequest(text=QA4_DESIGN_JD, job_title="Senior Graphic Designer"))
    assert len(res.required_skills) == 9
    expected = {
        "Adobe Photoshop", "Adobe Illustrator", "Figma", "After Effects",
        "Premiere Pro", "UI/UX Design", "Brand Identity", "Typography", "Motion Graphics"
    }
    assert set(res.required_skills) == expected
