"""Unit tests for RoleClassifier service."""

import pytest
from app.services.role_classifier import RoleClassifier


@pytest.fixture
def classifier() -> RoleClassifier:
    return RoleClassifier()


def test_model_loading_and_categories(classifier: RoleClassifier):
    categories = classifier.known_categories
    assert len(categories) == 24
    assert "ENGINEERING" in categories
    assert "INFORMATION-TECHNOLOGY" in categories
    assert "FINANCE" in categories


def test_valid_role_prediction_engineering(classifier: RoleClassifier):
    resume_text = (
        "Senior Software Engineer with experience in Python, C++, Linux kernel, "
        "and distributed systems architecture. Led engineering team of 10 developers."
    )
    res = classifier.predict_role(resume_text)
    assert res.predicted_role in classifier.known_categories
    assert 0.0 <= res.confidence <= 1.0
    assert res.confidence > 0.0


def test_valid_role_prediction_accountant(classifier: RoleClassifier):
    resume_text = (
        "Certified Accountant managing financial audits, tax compliance, ledger balances, "
        "and corporate accounting reports for enterprise clients."
    )
    res = classifier.predict_role(resume_text)
    assert res.predicted_role in classifier.known_categories
    assert 0.0 <= res.confidence <= 1.0


def test_empty_and_whitespace_input(classifier: RoleClassifier):
    res_empty = classifier.predict_role("")
    assert res_empty.predicted_role == "Unknown"
    assert res_empty.confidence == 0.0

    res_ws = classifier.predict_role("   \n\t ")
    assert res_ws.predicted_role == "Unknown"
    assert res_ws.confidence == 0.0

    res_none = classifier.predict_role(None)
    assert res_none.predicted_role == "Unknown"
    assert res_none.confidence == 0.0
