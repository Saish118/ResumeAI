"""Pytest configuration and shared fixtures for tests."""

import io
import fitz
import docx
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Provides a FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generates valid sample PDF file bytes with text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "John Doe\nSoftware Engineer\nExperience in Python, FastAPI, and Machine Learning."
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_docx_bytes() -> bytes:
    """Generates valid sample DOCX file bytes with text."""
    doc = docx.Document()
    doc.add_heading("Jane Smith", level=0)
    doc.add_paragraph("Senior Data Scientist with expertise in NLP, Python, and PyTorch.")
    stream = io.BytesIO()
    doc.save(stream)
    return stream.getvalue()
