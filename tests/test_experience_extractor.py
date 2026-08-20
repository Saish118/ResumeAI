"""Unit tests for ExperienceExtractor service."""

import pytest
from app.services.experience_extractor import ExperienceExtractor, experience_extractor


@pytest.fixture
def extractor() -> ExperienceExtractor:
    # Use fixed reference date (e.g. May 2026) for deterministic test results
    return ExperienceExtractor(current_year=2026, current_month=5)


def test_explicit_experience_statement(extractor: ExperienceExtractor):
    text = "Senior Software Engineer with 3+ years of experience in Python and FastAPI."
    result = extractor.extract_experience(text)
    assert result["candidate_experience_years"] == 3.0
    assert result["confidence"] in ("high", "medium")
    assert any("3+ years" in e for e in result["evidence"])


def test_clear_employment_date_range(extractor: ExperienceExtractor):
    text = """
    WORK EXPERIENCE
    Software Engineer | Acme Corp
    Jan 2022 - May 2024
    - Developed REST APIs in Python.
    """
    result = extractor.extract_experience(text)
    # Jan 2022 to May 2024 = 29 months = ~2.4 years
    assert result["candidate_experience_years"] is not None
    assert 2.3 <= result["candidate_experience_years"] <= 2.5
    assert result["confidence"] in ("high", "medium")
    assert len(result["evidence"]) > 0


def test_multiple_jobs_non_overlapping(extractor: ExperienceExtractor):
    text = """
    PROFESSIONAL EXPERIENCE
    Software Developer | Tech Corp
    Jan 2020 - Dec 2021

    Junior Developer | Startup Inc
    Jan 2018 - Dec 2019
    """
    result = extractor.extract_experience(text)
    # Jan 2018 - Dec 2019 (24 mos) + Jan 2020 - Dec 2021 (24 mos) = 48 mos = 4.0 years
    assert result["candidate_experience_years"] == 4.0
    assert result["confidence"] == "high"
    assert len(result["evidence"]) == 2


def test_multiple_jobs_with_overlapping_dates(extractor: ExperienceExtractor):
    text = """
    WORK EXPERIENCE
    Lead Engineer | Enterprise Co
    Jan 2021 - Dec 2023

    Consultant | Freelance
    Jun 2022 - Jun 2023
    """
    result = extractor.extract_experience(text)
    # Merged interval: Jan 2021 - Dec 2023 (36 mos = 3.0 years). Overlap is not double-counted.
    assert result["candidate_experience_years"] == 3.0
    assert result["confidence"] == "high"


def test_current_job_using_present(extractor: ExperienceExtractor):
    text = """
    EXPERIENCE
    Backend Engineer | Cloud Inc
    Jan 2024 - Present
    """
    # Jan 2024 to May 2026 (current_year=2026, current_month=5) = 29 months = ~2.4 years
    result = extractor.extract_experience(text)
    assert result["candidate_experience_years"] is not None
    assert 2.3 <= result["candidate_experience_years"] <= 2.5
    assert result["confidence"] in ("high", "medium")


def test_internship_only_resume(extractor: ExperienceExtractor):
    text = """
    EXPERIENCE
    Software Engineering Intern | Google
    Jun 2023 - Aug 2023
    - Built internal developer tools.
    """
    result = extractor.extract_experience(text)
    # Jun 2023 - Aug 2023 = 3 months = ~0.3 years
    assert result["candidate_experience_years"] is not None
    assert 0.2 <= result["candidate_experience_years"] <= 0.4
    assert result["confidence"] == "medium"
    assert len(result["evidence"]) > 0


def test_no_experience_information(extractor: ExperienceExtractor):
    text = """
    John Doe
    john@example.com

    EDUCATION
    BS in Computer Science - Tech University (2024)

    SKILLS
    Python, Java, Git
    """
    result = extractor.extract_experience(text)
    assert result["candidate_experience_years"] is None
    assert result["confidence"] == "low"
    assert result["evidence"] == []


def test_invalid_or_empty_text(extractor: ExperienceExtractor):
    assert extractor.extract_experience("")["candidate_experience_years"] is None
    assert extractor.extract_experience("   ")["candidate_experience_years"] is None
    assert extractor.extract_experience(None)["candidate_experience_years"] is None


def test_singleton_instance():
    res = experience_extractor.extract_experience("5 years of experience")
    assert res["candidate_experience_years"] == 5.0
