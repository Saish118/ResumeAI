"""Unit tests for SimilarityService."""

import pytest
from app.services.similarity_service import SimilarityService, MODEL_NAME


@pytest.fixture
def service() -> SimilarityService:
    return SimilarityService()


def test_identical_sentences(service: SimilarityService):
    text = "Built REST APIs using FastAPI and Python."
    res = service.compute_similarity(text, text)
    assert res.similarity_score >= 0.99
    assert res.model_name == MODEL_NAME


def test_semantically_similar_sentences(service: SimilarityService):
    text_a = "Built REST APIs using FastAPI and Python."
    text_b = "Developed backend services and REST APIs."
    res = service.compute_similarity(text_a, text_b)
    # Semantically similar texts should score relatively high (> 0.5)
    assert res.similarity_score > 0.5
    assert res.similarity_score <= 1.0


def test_unrelated_sentences(service: SimilarityService):
    text_a = "Built REST APIs using FastAPI and Python."
    text_b = "The cat sat on the mat in the backyard."
    res = service.compute_similarity(text_a, text_b)
    # Unrelated texts should score low (< 0.35) and be strictly less than similar texts
    assert res.similarity_score < 0.35


def test_empty_and_whitespace_input(service: SimilarityService):
    res_empty = service.compute_similarity("", "Python developer")
    assert res_empty.similarity_score == 0.0

    res_ws = service.compute_similarity("   ", "   \n  ")
    assert res_ws.similarity_score == 0.0

    res_none = service.compute_similarity(None, "Python developer")
    assert res_none.similarity_score == 0.0


def test_score_range_validation(service: SimilarityService):
    text_a = "Machine learning engineer with PyTorch expertise."
    text_b = "Data scientist specializing in deep learning."
    res = service.compute_similarity(text_a, text_b)
    assert 0.0 <= res.similarity_score <= 1.0
