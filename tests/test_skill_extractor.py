"""Unit tests for SkillExtractor service."""

import pytest
from app.services.skill_extractor import SkillExtractor


@pytest.fixture
def extractor() -> SkillExtractor:
    return SkillExtractor()


def test_canonical_skill_matching(extractor: SkillExtractor):
    text = "Developed services using Python and PostgreSQL."
    res = extractor.extract_skills(text)
    assert res.skills == ["Python", "PostgreSQL"]


def test_alias_matching(extractor: SkillExtractor):
    text = "Worked with postgres, sklearn, and reactjs."
    res = extractor.extract_skills(text)
    assert res.skills == ["PostgreSQL", "scikit-learn", "React"]


def test_case_insensitive_matching(extractor: SkillExtractor):
    text = "EXPERIENCE WITH PYTHON, REACT.JS, AND DOCKER."
    res = extractor.extract_skills(text)
    assert res.skills == ["Python", "React", "Docker"]


def test_duplicate_normalization(extractor: SkillExtractor):
    text = "Python, python, Python 3, py are all Python."
    res = extractor.extract_skills(text)
    assert res.skills == ["Python"]
    assert len(res.extracted_skills) == 1


def test_java_vs_javascript_false_positive_prevention(extractor: SkillExtractor):
    text = "Built applications using JavaScript and TypeScript."
    res = extractor.extract_skills(text)
    assert "JavaScript" in res.skills
    assert "TypeScript" in res.skills
    assert "Java" not in res.skills


def test_punctuation_sensitive_skills(extractor: SkillExtractor):
    text = "Expert in C++, C#, .NET, and Node.js backend development."
    res = extractor.extract_skills(text)
    assert res.skills == ["C++", "C#", ".NET", "Node.js"]


def test_multiple_categories(extractor: SkillExtractor):
    text = "Built ML models in PyTorch with FastAPI and deployed to AWS using Docker."
    res = extractor.extract_skills(text)
    categories = {s.category for s in res.extracted_skills}
    assert "Machine Learning / AI" in categories
    assert "Web Development" in categories
    assert "DevOps / Cloud" in categories


def test_empty_input(extractor: SkillExtractor):
    res = extractor.extract_skills("")
    assert res.skills == []
    assert res.extracted_skills == []

    res_none = extractor.extract_skills(None)
    assert res_none.skills == []
    assert res_none.extracted_skills == []


def test_text_containing_no_known_skills(extractor: SkillExtractor):
    text = "Responsible for managing team schedules, client calls, and weekly syncs."
    res = extractor.extract_skills(text)
    assert res.skills == []
    assert res.extracted_skills == []


def test_first_appearance_ordering(extractor: SkillExtractor):
    text = "Docker containerization for React app backed by Redis and Python."
    res = extractor.extract_skills(text)
    assert res.skills == ["Docker", "React", "Redis", "Python"]
