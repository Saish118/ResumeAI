"""Unit tests for SnippetExtractor service."""

# pyrefly: ignore [missing-import]
import pytest
from app.services.snippet_extractor import SnippetExtractor, snippet_extractor


@pytest.fixture
def extractor() -> SnippetExtractor:
    return SnippetExtractor()


def test_extract_snippets_bullet_points(extractor: SnippetExtractor):
    raw_text = """
    EXPERIENCE
    • Developed backend REST microservices using Python and FastAPI.
    - Built responsive web dashboards using React, HTML5, and CSS.
    * Implemented data ingestion pipelines using MongoDB and Redis.
    """
    snippets = extractor.extract_snippets_from_text(raw_text)

    assert "Developed backend REST microservices using Python and FastAPI." in snippets
    assert "Built responsive web dashboards using React, HTML5, and CSS." in snippets
    assert "Implemented data ingestion pipelines using MongoDB and Redis." in snippets
    # Confirm section header is filtered out
    assert "EXPERIENCE" not in snippets


def test_extract_snippets_long_paragraph_sentence_splitting(extractor: SnippetExtractor):
    long_para = (
        "Architected scalable backend infrastructure. "
        "Developed an AI-based vehicle surveillance system using Python, YOLOv5, EasyOCR and MongoDB. "
        "Engineered real-time computer vision inference modules for edge computing devices."
    )
    # Paragraph total length is > 200 chars
    snippets = extractor.extract_snippets_from_text(long_para)

    assert len(snippets) >= 2
    assert "Developed an AI-based vehicle surveillance system using Python, YOLOv5, EasyOCR and MongoDB." in snippets


def test_extract_snippets_header_and_noise_filtering(extractor: SnippetExtractor):
    raw = """
    TECHNICAL SKILLS
    
    Python, FastAPI, MongoDB, React
    
    WORK EXPERIENCE
    
    Page 1
    john.doe@example.com
    +1 (555) 019-2831
    """
    snippets = extractor.extract_snippets_from_text(raw)

    assert "TECHNICAL SKILLS" not in snippets
    assert "WORK EXPERIENCE" not in snippets
    assert "john.doe@example.com" not in snippets
    assert "Python, FastAPI, MongoDB, React" in snippets


def test_extract_snippets_deduplication(extractor: SnippetExtractor):
    raw = """
    Developed backend services using Python and FastAPI.
    Developed backend services using Python and FastAPI.
    """
    snippets = extractor.extract_snippets_from_text(raw)
    assert len(snippets) == 1
    assert snippets[0] == "Developed backend services using Python and FastAPI."


def test_extract_snippets_empty_and_none(extractor: SnippetExtractor):
    assert extractor.extract_snippets_from_text(None) == []
    assert extractor.extract_snippets_from_text("") == []
    assert extractor.extract_snippets_from_text("   \n\t  ") == []
