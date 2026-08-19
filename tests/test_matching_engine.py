"""Unit tests for MatchingEngine service."""

import pytest
from app.schemas.job import JobRequirementDetail
from app.schemas.match import MatchRequest, ResumeDataInput, JobDataInput
from app.schemas.skill import SkillDetail
from app.services.matching_engine import MatchingEngine


@pytest.fixture
def engine() -> MatchingEngine:
    return MatchingEngine()


def test_all_required_skills_matched(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "PostgreSQL"],
            extracted_skills=[
                SkillDetail(skill="Python", matched_alias="Python", category="Programming Languages", evidence="Built APIs using Python."),
                SkillDetail(skill="FastAPI", matched_alias="FastAPI", category="Web Development", evidence="Developed backend in FastAPI."),
                SkillDetail(skill="PostgreSQL", matched_alias="PostgreSQL", category="Databases", evidence="Managed PostgreSQL databases.")
            ]
        ),
        job=JobDataInput(
            job_title="Python Developer",
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            preferred_skills=[],
            requirements=[
                JobRequirementDetail(skill="Python", requirement_type="required", evidence="Python backend experience required."),
                JobRequirementDetail(skill="FastAPI", requirement_type="required", evidence="FastAPI framework experience required.")
            ]
        )
    )
    res = engine.match(req)
    assert res.matched_required_skills == ["Python", "FastAPI", "PostgreSQL"]
    assert res.missing_required_skills == []
    assert res.overall_score >= 90.0
    assert 0.0 <= res.overall_score <= 100.0


def test_some_required_skills_missing(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(skills=["Python"]),
        job=JobDataInput(
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            preferred_skills=[]
        )
    )
    res = engine.match(req)
    assert res.matched_required_skills == ["Python"]
    assert set(res.missing_required_skills) == {"FastAPI", "PostgreSQL"}
    assert res.overall_score < 70.0


def test_preferred_skill_matching(engine: MatchingEngine):
    req_base = MatchRequest(
        resume=ResumeDataInput(skills=["Python"]),
        job=JobDataInput(required_skills=["Python"], preferred_skills=["Docker", "AWS"])
    )
    res_base = engine.match(req_base)

    req_with_pref = MatchRequest(
        resume=ResumeDataInput(skills=["Python", "Docker", "AWS"]),
        job=JobDataInput(required_skills=["Python"], preferred_skills=["Docker", "AWS"])
    )
    res_with_pref = engine.match(req_with_pref)

    assert res_with_pref.overall_score > res_base.overall_score
    assert res_with_pref.matched_preferred_skills == ["Docker", "AWS"]


def test_required_vs_preferred_weighting(engine: MatchingEngine):
    # Candidate A matches required skills (Python) but misses preferred (Docker)
    req_a = MatchRequest(
        resume=ResumeDataInput(skills=["Python"]),
        job=JobDataInput(required_skills=["Python"], preferred_skills=["Docker"])
    )
    res_a = engine.match(req_a)

    # Candidate B misses required skill (Python) but matches preferred (Docker)
    req_b = MatchRequest(
        resume=ResumeDataInput(skills=["Docker"]),
        job=JobDataInput(required_skills=["Python"], preferred_skills=["Docker"])
    )
    res_b = engine.match(req_b)

    # Matching required skills should contribute significantly more than preferred skills
    assert res_a.overall_score > res_b.overall_score


def test_experience_meets_requirement(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(skills=["Python"], candidate_experience_years=4),
        job=JobDataInput(required_skills=["Python"], minimum_experience_years=3)
    )
    res = engine.match(req)
    assert res.experience_assessment.meets_requirement is True
    assert res.experience_assessment.status == "matched"


def test_experience_below_requirement(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(skills=["Python"], candidate_experience_years=1),
        job=JobDataInput(required_skills=["Python"], minimum_experience_years=5)
    )
    res = engine.match(req)
    assert res.experience_assessment.meets_requirement is False
    assert res.experience_assessment.status == "below_requirement"


def test_experience_unavailable(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(skills=["Python"], candidate_experience_years=None),
        job=JobDataInput(required_skills=["Python"], minimum_experience_years=3)
    )
    res = engine.match(req)
    assert res.experience_assessment.meets_requirement is None
    assert res.experience_assessment.status == "unknown"
    assert 0.0 <= res.overall_score <= 100.0


def test_semantic_evidence_matching(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python"],
            extracted_skills=[
                SkillDetail(skill="Python", matched_alias="Python", category="Programming Languages", evidence="Built high-throughput REST APIs using FastAPI and Python.")
            ]
        ),
        job=JobDataInput(
            required_skills=["Python"],
            requirements=[
                JobRequirementDetail(skill="Python", requirement_type="required", evidence="Developed scalable backend services and REST APIs.")
            ]
        )
    )
    res = engine.match(req)
    assert len(res.semantic_evidence_matches) == 1
    match_item = res.semantic_evidence_matches[0]
    assert match_item.requirement_skill == "Python"
    assert match_item.best_matching_resume_evidence == "Built high-throughput REST APIs using FastAPI and Python."
    assert match_item.similarity_score > 0.5


def test_unrelated_semantic_evidence(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Git"],
            extracted_skills=[
                SkillDetail(skill="Git", matched_alias="Git", category="Tools", evidence="Managed source code repositories in Git.")
            ]
        ),
        job=JobDataInput(
            required_skills=["Machine Learning"],
            requirements=[
                JobRequirementDetail(skill="Machine Learning", requirement_type="required", evidence="Deep learning model training and hyperparameter tuning.")
            ]
        )
    )
    res = engine.match(req)
    assert len(res.semantic_evidence_matches) == 1
    match_item = res.semantic_evidence_matches[0]
    assert match_item.similarity_score < 0.40


def test_zero_or_empty_requirements(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(skills=[]),
        job=JobDataInput(required_skills=[], preferred_skills=[], requirements=[])
    )
    res = engine.match(req)
    assert res.overall_score == 100.0
    assert res.matched_required_skills == []
    assert res.missing_required_skills == []
