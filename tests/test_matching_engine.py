"""Unit tests for MatchingEngine service and requirement-level semantic evidence."""

# pyrefly: ignore [missing-import]
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
    req_a = MatchRequest(
        resume=ResumeDataInput(skills=["Python"]),
        job=JobDataInput(required_skills=["Python"], preferred_skills=["Docker"])
    )
    res_a = engine.match(req_a)

    req_b = MatchRequest(
        resume=ResumeDataInput(skills=["Docker"]),
        job=JobDataInput(required_skills=["Python"], preferred_skills=["Docker"])
    )
    res_b = engine.match(req_b)

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
                JobRequirementDetail(skill="Python", requirement_type="required", evidence="Developed scalable backend services and REST APIs in Python.")
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
    # Unrelated match should be None due to thresholding
    assert match_item.best_matching_resume_evidence is None
    assert match_item.similarity_score == 0.0


def test_zero_or_empty_requirements(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(skills=[]),
        job=JobDataInput(required_skills=[], preferred_skills=[], requirements=[])
    )
    res = engine.match(req)
    assert res.overall_score == 100.0
    assert res.matched_required_skills == []
    assert res.missing_required_skills == []


# ==============================================================================
# SPECIFIC REQUIREMENT-LEVEL EVIDENCE QUALITY TESTS
# ==============================================================================

def test_python_requirement_finds_python_evidence(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            raw_text="• Developed backend microservices using Python and FastAPI.\n• Created database schemas using MongoDB."
        ),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="Python", requirement_type="required", evidence="Strong experience with Python server-side development.")
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert item.requirement_skill == "Python"
    assert item.best_matching_resume_evidence == "Developed backend microservices using Python and FastAPI."
    assert item.similarity_score > 0.40


def test_mongodb_requirement_finds_mongodb_evidence(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            raw_text="• Built responsive web interfaces in React.\n• Managed data storage and index tuning using MongoDB."
        ),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="MongoDB", requirement_type="required", evidence="Database administration and queries using MongoDB.")
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert item.requirement_skill == "MongoDB"
    assert item.best_matching_resume_evidence == "Managed data storage and index tuning using MongoDB."
    assert item.similarity_score > 0.40


def test_react_requirement_finds_react_evidence(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            raw_text="• Developed RESTful backend APIs in Python.\n• Built web applications with React and Redux."
        ),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="React", requirement_type="required", evidence="Frontend web development using React framework.")
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert item.requirement_skill == "React"
    assert item.best_matching_resume_evidence == "Built web applications with React and Redux."
    assert item.similarity_score > 0.40


def test_unrelated_requirement_does_not_use_python_evidence(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            raw_text="• Developed backend services using Python and FastAPI."
        ),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="Git", requirement_type="required", evidence="Proficient in Git version control and GitHub workflow.")
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert item.requirement_skill == "Git"
    assert item.best_matching_resume_evidence is None
    assert item.similarity_score == 0.0


def test_long_resume_text_split_into_usable_snippets(engine: MatchingEngine):
    resume_text = """
    EXPERIENCE
    • Developed AI surveillance systems using Python and YOLOv5.
    • Optimized database queries in PostgreSQL for enterprise software.
    • Implemented automated CI/CD pipelines with GitHub Actions.
    """
    req = MatchRequest(
        resume=ResumeDataInput(raw_text=resume_text),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="Python", requirement_type="required", evidence="Python development experience required.")
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert item.best_matching_resume_evidence == "Developed AI surveillance systems using Python and YOLOv5."


def test_long_paragraphs_constrained_to_sensible_evidence_snippets(engine: MatchingEngine):
    long_para = (
        "Architected scalable cloud backend systems for financial analytics. "
        "Developed machine learning models using Python and Scikit-Learn to forecast transaction volume. "
        "Managed database cluster deployment on Amazon AWS EC2 instances."
    )
    req = MatchRequest(
        resume=ResumeDataInput(raw_text=long_para),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="Python", requirement_type="required", evidence="Building machine learning pipelines in Python.")
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert "Developed machine learning models using Python and Scikit-Learn" in item.best_matching_resume_evidence
    assert len(item.best_matching_resume_evidence) < 150


def test_no_strong_semantic_match_returns_no_evidence(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(
            raw_text="• Built responsive web user interfaces using HTML and CSS."
        ),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="Rust", requirement_type="required", evidence="Systems programming experience in Rust.")
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert item.best_matching_resume_evidence is None
    assert item.similarity_score == 0.0


def test_existing_exact_skill_matching_still_works(engine: MatchingEngine):
    req = MatchRequest(
        resume=ResumeDataInput(skills=["Python", "React", "MongoDB"]),
        job=JobDataInput(
            required_skills=["Python", "MongoDB"],
            preferred_skills=["React", "Docker"]
        )
    )
    res = engine.match(req)
    assert res.matched_required_skills == ["Python", "MongoDB"]
    assert res.missing_required_skills == []
    assert res.matched_preferred_skills == ["React"]
    assert res.missing_preferred_skills == ["Docker"]


def test_multiple_requirements_legitimately_use_one_multi_technology_sentence(engine: MatchingEngine):
    multi_tech_sentence = "Developed an AI-based vehicle surveillance system using Python, YOLOv5, EasyOCR and MongoDB."
    req = MatchRequest(
        resume=ResumeDataInput(raw_text=multi_tech_sentence),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="Python", requirement_type="required", evidence="Python programming experience."),
                JobRequirementDetail(skill="MongoDB", requirement_type="required", evidence="Data persistence using MongoDB database."),
                JobRequirementDetail(skill="Computer Vision", requirement_type="required", evidence="Computer vision model inference with YOLOv5.")
            ]
        )
    )
    res = engine.match(req)
    matches_dict = {m.requirement_skill: m.best_matching_resume_evidence for m in res.semantic_evidence_matches}
    assert matches_dict["Python"] == multi_tech_sentence
    assert matches_dict["MongoDB"] == multi_tech_sentence
    assert matches_dict["Computer Vision"] == multi_tech_sentence


def test_job_description_text_never_returned_as_resume_evidence(engine: MatchingEngine):
    jd_req_text = "Job description specific requirement for cloud microservice deployment on AWS."
    req = MatchRequest(
        resume=ResumeDataInput(raw_text="• Developed REST APIs using Python and FastAPI."),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="AWS", requirement_type="required", evidence=jd_req_text)
            ]
        )
    )
    res = engine.match(req)
    item = res.semantic_evidence_matches[0]
    assert item.best_matching_resume_evidence != jd_req_text
    assert item.best_matching_resume_evidence is None


def test_realistic_resume_regression(engine: MatchingEngine):
    realistic_resume = """
    SUMMARY
    Senior Full Stack & AI Engineer with 5+ years of experience building web applications and ML systems.
    
    WORK EXPERIENCE
    • Engineered backend microservices using Python, FastAPI, and PostgreSQL for high-traffic API services.
    • Developed responsive frontend client interfaces using JavaScript, React, and Tailwind CSS.
    • Designed data storage architectures using MongoDB for unstructured event logging.
    • Implemented real-time object detection and computer vision solutions using PyTorch, OpenCV, and Computer Vision algorithms.
    • Automated codebase collaboration, version control, and CI/CD pipelines using Git and GitHub.
    """

    job = JobDataInput(
        required_skills=["Python", "React", "MongoDB", "Computer Vision", "Git"],
        requirements=[
            JobRequirementDetail(skill="Python", requirement_type="required", evidence="Backend API development experience in Python."),
            JobRequirementDetail(skill="React", requirement_type="required", evidence="Frontend UI construction with React framework."),
            JobRequirementDetail(skill="MongoDB", requirement_type="required", evidence="NoSQL database design using MongoDB."),
            JobRequirementDetail(skill="Computer Vision", requirement_type="required", evidence="Deep learning and Computer Vision model training."),
            JobRequirementDetail(skill="Git", requirement_type="required", evidence="Source control management with Git and GitHub."),
        ]
    )

    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "JavaScript", "React", "MongoDB", "Computer Vision", "Git"],
            raw_text=realistic_resume
        ),
        job=job
    )

    res = engine.match(req)
    matches_dict = {m.requirement_skill: m for m in res.semantic_evidence_matches}

    assert "Python" in matches_dict["Python"].best_matching_resume_evidence
    assert "React" in matches_dict["React"].best_matching_resume_evidence
    assert "MongoDB" in matches_dict["MongoDB"].best_matching_resume_evidence
    assert "Computer Vision" in matches_dict["Computer Vision"].best_matching_resume_evidence or "PyTorch" in matches_dict["Computer Vision"].best_matching_resume_evidence
    assert "Git" in matches_dict["Git"].best_matching_resume_evidence

    # Confirm distinct requirement-specific evidence snippets were retrieved
    evidence_set = set(m.best_matching_resume_evidence for m in res.semantic_evidence_matches)
    assert len(evidence_set) >= 4  # At least 4 distinct sentences retrieved across 5 distinct requirements!


def test_snippet_exact_substring_traceability(engine: MatchingEngine):
    original_resume = """
    SUMMARY
    Software engineer with 3+ years of experience building backend APIs and web applications.

    WORK EXPERIENCE
    • Engineered backend microservices using Python, FastAPI, and PostgreSQL for high-traffic REST API services.
    • Developed responsive web user interfaces using JavaScript, React, and Tailwind CSS.
    • Managed document-oriented database storage and indexing using MongoDB.
    • Implemented computer vision pipelines using YOLOv5, OpenCV, and PyTorch for real-time video surveillance.
    • Maintained version control, branching models, and release pipelines using Git and GitHub.
    """

    job = JobDataInput(
        required_skills=["Python", "React", "MongoDB", "Computer Vision", "PyTorch", "Git", "REST API"],
        requirements=[
            JobRequirementDetail(skill="Python", requirement_type="required", evidence="Python backend experience."),
            JobRequirementDetail(skill="React", requirement_type="required", evidence="React web development."),
            JobRequirementDetail(skill="MongoDB", requirement_type="required", evidence="MongoDB database experience."),
            JobRequirementDetail(skill="Computer Vision", requirement_type="required", evidence="Computer vision model inference."),
            JobRequirementDetail(skill="PyTorch", requirement_type="required", evidence="PyTorch deep learning."),
            JobRequirementDetail(skill="Git", requirement_type="required", evidence="Git version control."),
            JobRequirementDetail(skill="REST API", requirement_type="required", evidence="REST API development."),
        ]
    )

    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "React", "MongoDB", "Computer Vision", "PyTorch", "Git", "REST API"],
            raw_text=original_resume
        ),
        job=job
    )

    res = engine.match(req)
    normalized_original = " ".join(original_resume.split())

    for item in res.semantic_evidence_matches:
        if item.best_matching_resume_evidence:
            evidence_str = item.best_matching_resume_evidence
            normalized_evidence = " ".join(evidence_str.split())

            # Traceability assertion: every returned snippet MUST be an exact substring of the original text
            assert normalized_evidence in normalized_original, f"Snippet '{evidence_str}' is not a clean substring of original resume text."

            # Integrity assertion: snippet must not be a truncated fragment starting or ending mid-word
            assert not evidence_str.startswith(("ter ", "sion", "ing ")), f"Snippet '{evidence_str}' appears to be a truncated fragment."
            assert len(evidence_str.split()) >= 3

    # Verify REST API requirement receives specific implementation bullet over generic summary
    rest_match = next(m for m in res.semantic_evidence_matches if m.requirement_skill == "REST API")
    assert "Engineered backend microservices" in rest_match.best_matching_resume_evidence


def test_similarity_score_clamping_and_overflow_regression(engine: MatchingEngine):
    """
    Regression test verifying that similarity scores NEVER exceed 1.0 even when
    combining semantic similarity, skill presence boost, and multi-keyword API relevance boosts.
    """
    resume_text = "Engineered backend microservices using Python, FastAPI, and PostgreSQL for high-traffic REST API services."

    job = JobDataInput(
        required_skills=["Python", "FastAPI", "REST API"],
        requirements=[
            JobRequirementDetail(skill="Python", requirement_type="required", evidence="Python backend microservices development."),
            JobRequirementDetail(skill="FastAPI", requirement_type="required", evidence="FastAPI framework microservices REST APIs."),
            JobRequirementDetail(skill="REST API", requirement_type="required", evidence="Experience developing REST APIs, backend microservices, and API services."),
            JobRequirementDetail(skill="Kubernetes", requirement_type="required", evidence="Kubernetes container management."),
        ]
    )

    req = MatchRequest(
        resume=ResumeDataInput(
            skills=["Python", "FastAPI", "REST API"],
            raw_text=resume_text
        ),
        job=job
    )

    res = engine.match(req)

    for item in res.semantic_evidence_matches:
        # Bounded score assertions: 0.0 <= similarity_score <= 1.0
        assert 0.0 <= item.similarity_score <= 1.0, f"Score for {item.requirement_skill} overflowed: {item.similarity_score}"

    # Specific check for Python, FastAPI, REST API (formerly > 1.0)
    scores_dict = {m.requirement_skill: m.similarity_score for m in res.semantic_evidence_matches}
    assert scores_dict["Python"] <= 1.0
    assert scores_dict["FastAPI"] <= 1.0
    assert scores_dict["REST API"] <= 1.0
    assert scores_dict["Kubernetes"] == 0.0


def test_score_bounding_edge_cases(engine: MatchingEngine):
    """Tests normal, strong boost, multiple boosts, and missing requirement boundaries."""
    resume_text = "Built high-performance microservices using FastAPI, REST APIs, backend services, and Python."
    req = MatchRequest(
        resume=ResumeDataInput(skills=["FastAPI"], raw_text=resume_text),
        job=JobDataInput(
            requirements=[
                JobRequirementDetail(skill="FastAPI", requirement_type="required", evidence="FastAPI REST API microservices"),
                JobRequirementDetail(skill="Rust", requirement_type="required", evidence="Rust systems programming")
            ]
        )
    )
    res = engine.match(req)

    fastapi_match = next(m for m in res.semantic_evidence_matches if m.requirement_skill == "FastAPI")
    rust_match = next(m for m in res.semantic_evidence_matches if m.requirement_skill == "Rust")

    # 1. Normal/boosted score is strictly <= 1.0
    assert 0.0 <= fastapi_match.similarity_score <= 1.0
    # 2. Missing requirement returns exactly 0.0
    assert rust_match.similarity_score == 0.0
    assert rust_match.best_matching_resume_evidence is None


