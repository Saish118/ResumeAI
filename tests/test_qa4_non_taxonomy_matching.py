"""Regression tests for QA4 non-taxonomy skill extraction and matching."""

# pyrefly: ignore [missing-import]
import pytest
from fastapi.testclient import TestClient
from app.schemas.job import JobProcessRequest, JobRequirementDetail
from app.schemas.match import MatchRequest, ResumeDataInput, JobDataInput
from app.services.job_processor import JobProcessor, job_processor
from app.services.matching_engine import MatchingEngine, matching_engine

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

QA4_CANDIDATE_RESUME_TEXT = """
SUMMARY
Software engineer with 3.7 years of experience building backend APIs and web applications.

SKILLS
Python, FastAPI, React, MongoDB, PostgreSQL, Git, GitHub

EXPERIENCE
• Developed scalable backend microservices using Python and FastAPI.
• Built frontend components using React and CSS.
• Managed PostgreSQL and MongoDB databases.
• Maintained codebase version control with Git.
"""


def test_qa4_all_9_non_taxonomy_skills_preserved():
    res = job_processor.process_job_description(JobProcessRequest(text=QA4_DESIGN_JD, job_title="Senior Graphic Designer"))
    assert res.job_title == "Senior Graphic Designer"

    assert res.minimum_experience_years == 5
    assert len(res.required_skills) == 9
    expected_skills = {
        "Adobe Photoshop", "Adobe Illustrator", "Figma", "After Effects",
        "Premiere Pro", "UI/UX Design", "Brand Identity", "Typography", "Motion Graphics"
    }
    assert set(res.required_skills) == expected_skills

    non_tax_details = [r for r in res.requirements if not r.recognized_by_taxonomy]
    assert len(non_tax_details) == 9
    for detail in non_tax_details:
        assert detail.canonical_name is None
        assert detail.recognized_by_taxonomy is False


def test_qa4_software_engineer_candidate_matches_0_missing_9():
    processed_job = job_processor.process_job_description(JobProcessRequest(text=QA4_DESIGN_JD))
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "React", "MongoDB", "Git"],
            candidate_experience_years=3.7,
            raw_text=QA4_CANDIDATE_RESUME_TEXT,
        ),
        job=JobDataInput(
            job_title=processed_job.job_title,
            required_skills=processed_job.required_skills,
            preferred_skills=processed_job.preferred_skills,
            minimum_experience_years=processed_job.minimum_experience_years,
            requirements=processed_job.requirements,
        )
    )
    result = matching_engine.match(req)
    assert len(result.matched_required_skills) == 0
    assert len(result.missing_required_skills) == 9
    assert result.experience_assessment.meets_requirement is False
    assert result.experience_assessment.status == "below_requirement"
    assert result.overall_score < 35.0


def test_non_taxonomy_skill_does_not_disappear():
    jd_text = "Required: AutoCAD and Salesforce."
    res = job_processor.process_job_description(JobProcessRequest(text=jd_text))
    assert "AutoCAD" in res.required_skills
    assert "Salesforce" in res.required_skills
    autocad_req = next(r for r in res.requirements if r.skill == "AutoCAD")
    assert autocad_req.recognized_by_taxonomy is False


def test_candidate_explicitly_mentions_non_taxonomy_skill_matches():
    processed_job = job_processor.process_job_description(JobProcessRequest(text=QA4_DESIGN_JD))
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI"],
            raw_text="Experienced designer proficient in Adobe Photoshop and Figma with 6 years experience.",
            candidate_experience_years=6.0,
        ),
        job=JobDataInput(
            job_title=processed_job.job_title,
            required_skills=processed_job.required_skills,
            preferred_skills=processed_job.preferred_skills,
            minimum_experience_years=processed_job.minimum_experience_years,
            requirements=processed_job.requirements,
        )
    )
    result = matching_engine.match(req)
    assert "Adobe Photoshop" in result.matched_required_skills
    assert "Figma" in result.matched_required_skills
    assert "Adobe Photoshop" not in result.missing_required_skills
    assert "Figma" not in result.missing_required_skills


def test_photoshop_absent_no_semantic_evidence_false_positive():
    processed_job = job_processor.process_job_description(JobProcessRequest(text=QA4_DESIGN_JD))
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "React", "MongoDB"],
            raw_text=QA4_CANDIDATE_RESUME_TEXT,
        ),
        job=JobDataInput(
            job_title=processed_job.job_title,
            required_skills=processed_job.required_skills,
            preferred_skills=processed_job.preferred_skills,
            minimum_experience_years=processed_job.minimum_experience_years,
            requirements=processed_job.requirements,
        )
    )
    result = matching_engine.match(req)
    ps_match = next(m for m in result.semantic_evidence_matches if m.requirement_skill == "Adobe Photoshop")
    assert ps_match.best_matching_resume_evidence is None
    assert ps_match.similarity_score == 0.0


def test_figma_absent_no_semantic_evidence_false_positive():
    processed_job = job_processor.process_job_description(JobProcessRequest(text=QA4_DESIGN_JD))
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "React", "MongoDB"],
            raw_text=QA4_CANDIDATE_RESUME_TEXT,
        ),
        job=JobDataInput(
            job_title=processed_job.job_title,
            required_skills=processed_job.required_skills,
            preferred_skills=processed_job.preferred_skills,
            minimum_experience_years=processed_job.minimum_experience_years,
            requirements=processed_job.requirements,
        )
    )
    result = matching_engine.match(req)
    figma_match = next(m for m in result.semantic_evidence_matches if m.requirement_skill == "Figma")
    assert figma_match.best_matching_resume_evidence is None
    assert figma_match.similarity_score == 0.0


def test_existing_python_react_mongodb_matching_still_passes():
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "React", "MongoDB", "Git"],
            candidate_experience_years=4.0
        ),
        job=JobDataInput(
            job_title="Fullstack Developer",
            required_skills=["Python", "React", "MongoDB"],
            preferred_skills=["Git"],
            minimum_experience_years=3
        )
    )
    result = matching_engine.match(req)
    assert set(result.matched_required_skills) == {"Python", "React", "MongoDB"}
    assert result.matched_preferred_skills == ["Git"]
    assert result.overall_score >= 90.0


def test_empty_or_title_only_jd_still_returns_400(client: TestClient):
    resp_empty = client.post("/api/v1/job-description/process", json={"text": ""})
    assert resp_empty.status_code == 400

    resp_title = client.post("/api/v1/job-description/process", json={"text": "Job Title: Software Developer"})
    assert resp_title.status_code == 400


def test_experience_requirement_evaluated_independently():
    req_meets = MatchRequest(
        resume=ResumeDataInput(skills=["Python"], candidate_experience_years=5.0),
        job=JobDataInput(required_skills=["Python"], minimum_experience_years=3)
    )
    res_meets = matching_engine.match(req_meets)
    assert res_meets.experience_assessment.meets_requirement is True

    req_below = MatchRequest(
        resume=ResumeDataInput(skills=["Python"], candidate_experience_years=2.0),
        job=JobDataInput(required_skills=["Python"], minimum_experience_years=5)
    )
    res_below = matching_engine.match(req_below)
    assert res_below.experience_assessment.meets_requirement is False


def test_overall_score_for_qa4_is_low():
    processed_job = job_processor.process_job_description(JobProcessRequest(text=QA4_DESIGN_JD))
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "React", "MongoDB"],
            candidate_experience_years=3.7,
            raw_text=QA4_CANDIDATE_RESUME_TEXT,
        ),
        job=JobDataInput(
            job_title=processed_job.job_title,
            required_skills=processed_job.required_skills,
            preferred_skills=processed_job.preferred_skills,
            minimum_experience_years=processed_job.minimum_experience_years,
            requirements=processed_job.requirements,
        )
    )
    result = matching_engine.match(req)
    assert result.overall_score < 35.0
    assert result.overall_score >= 0.0
