"""Integration tests for POST /api/v1/resume/parse API endpoint and health endpoints."""

from fastapi.testclient import TestClient


def test_parse_resume_endpoint_pdf_success(client: TestClient, sample_pdf_bytes: bytes):
    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("john_doe_resume.pdf", sample_pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "john_doe_resume.pdf"
    assert data["file_type"] == "pdf"
    assert "John Doe" in data["extracted_text"]
    assert data["character_count"] > 0
    assert data["page_count"] == 1


def test_parse_resume_endpoint_docx_success(client: TestClient, sample_docx_bytes: bytes):
    response = client.post(
        "/api/v1/resume/parse",
        files={
            "file": (
                "jane_smith_resume.docx",
                sample_docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "jane_smith_resume.docx"
    assert data["file_type"] == "docx"
    assert "Jane Smith" in data["extracted_text"]
    assert data["character_count"] > 0
    assert data["page_count"] is None


def test_parse_resume_endpoint_unsupported_file_type(client: TestClient):
    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("resume.txt", b"Plain text resume content", "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported file format '.txt'" in data["detail"]


def test_parse_resume_endpoint_empty_file(client: TestClient):
    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("empty_resume.pdf", b"", "application/pdf")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "empty" in data["detail"].lower()


def test_parse_resume_endpoint_corrupt_file(client: TestClient):
    response = client.post(
        "/api/v1/resume/parse",
        files={"file": ("corrupt.pdf", b"Invalid binary data", "application/pdf")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Failed to open PDF document" in data["detail"]


def test_health_endpoints_remain_functional(client: TestClient):
    root_res = client.get("/health")
    assert root_res.status_code == 200
    assert root_res.json()["status"] == "healthy"

    v1_res = client.get("/api/v1/health")
    assert v1_res.status_code == 200
    assert v1_res.json()["status"] == "healthy"
