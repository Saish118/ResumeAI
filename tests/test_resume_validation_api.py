"""API Integration tests for Resume Content Validation."""

import io
import docx
import fitz
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.models import ResumeAnalysis

client = TestClient(app)


def _make_docx_bytes(text: str) -> bytes:
    doc = docx.Document()
    for line in text.strip().split("\n"):
        doc.add_paragraph(line)
    stream = io.BytesIO()
    doc.save(stream)
    return stream.getvalue()


def _make_pdf_bytes(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_api_parse_rejects_non_resume_invoice(db_isolation: Session):
    text = """
    TAX INVOICE # 94021
    Bill To: Global Logistics Inc.
    Ship To: Warehouse 4B
    Invoice Date: Oct 12, 2025
    Payment Terms: Net 30
    Amount Due: $3,000.00
    Total Amount: $3,000.00
    """
    docx_bytes = _make_docx_bytes(text)
    initial_count = db_isolation.query(ResumeAnalysis).count()

    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("invoice.docx", io.BytesIO(docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "This document does not appear to be a resume" in detail

    # Verify no record was inserted into database
    new_count = db_isolation.query(ResumeAnalysis).count()
    assert new_count == initial_count


def test_api_parse_rejects_academic_paper(db_isolation: Session):
    text = """
    Deep Learning for Image Recognition
    Abstract: Convolutional networks have achieved state of the art results.
    1. Introduction
    Image classification is a core problem in computer vision.
    2. Methodology
    We train a ResNet-50 model on ImageNet.
    References:
    [1] LeCun et al. IEEE Transactions 1998. doi:10.1109/TNN.1998
    """
    pdf_bytes = _make_pdf_bytes(text)
    initial_count = db_isolation.query(ResumeAnalysis).count()

    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("research_paper.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "This document does not appear to be a resume" in detail

    # Verify no record was inserted into database
    new_count = db_isolation.query(ResumeAnalysis).count()
    assert new_count == initial_count


def test_api_parse_accepts_valid_resume(db_isolation: Session):
    text = """
    JOHN DOE
    john.doe@example.com | 555-0199 | github.com/johndoe
    
    SUMMARY
    Software engineer with experience in Python and web development.
    
    EDUCATION
    BS Computer Science, State University (2020 - 2024)
    
    SKILLS
    Python, FastAPI, SQL, Git, React
    
    EXPERIENCE
    Software Engineering Intern - Acme Software (2023 - 2024)
    Developed REST APIs using Python and FastAPI.
    """
    docx_bytes = _make_docx_bytes(text)
    initial_count = db_isolation.query(ResumeAnalysis).count()

    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("john_doe_resume.docx", io.BytesIO(docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "john_doe_resume.docx"
    assert "extracted_text" in data

    # Verify record WAS saved to database
    new_count = db_isolation.query(ResumeAnalysis).count()
    assert new_count == initial_count + 1
