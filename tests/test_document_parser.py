"""Unit tests for document validator and document parser service."""

import pytest
from app.services.document_validator import validate_resume_file, DocumentValidationError
from app.services.document_parser import (
    parse_resume_document,
    extract_pdf_text,
    extract_docx_text,
    DocumentParsingError,
)


def test_validate_resume_file_valid_pdf(sample_pdf_bytes: bytes):
    filename, file_type = validate_resume_file("my_resume.pdf", sample_pdf_bytes)
    assert filename == "my_resume.pdf"
    assert file_type == "pdf"


def test_validate_resume_file_valid_docx(sample_docx_bytes: bytes):
    filename, file_type = validate_resume_file("my_resume.DOCX", sample_docx_bytes)
    assert filename == "my_resume.DOCX"
    assert file_type == "docx"


def test_validate_resume_file_unsupported_extension():
    with pytest.raises(DocumentValidationError) as exc_info:
        validate_resume_file("resume.txt", b"Hello world")
    assert "Unsupported file format '.txt'" in str(exc_info.value)


def test_validate_resume_file_empty_content():
    with pytest.raises(DocumentValidationError) as exc_info:
        validate_resume_file("resume.pdf", b"")
    assert "Uploaded file is empty" in str(exc_info.value)


def test_extract_pdf_text_success(sample_pdf_bytes: bytes):
    text, page_count = extract_pdf_text(sample_pdf_bytes)
    assert "John Doe" in text
    assert "Software Engineer" in text
    assert page_count == 1


def test_extract_docx_text_success(sample_docx_bytes: bytes):
    text, page_count = extract_docx_text(sample_docx_bytes)
    assert "Jane Smith" in text
    assert "Senior Data Scientist" in text
    assert page_count is None


def test_extract_pdf_corrupted_content():
    with pytest.raises(DocumentParsingError):
        extract_pdf_text(b"%PDF-1.4 invalid corrupt content")


def test_extract_docx_corrupted_content():
    with pytest.raises(DocumentParsingError):
        extract_docx_text(b"PK corrupt docx binary content")


def test_parse_resume_document_pdf(sample_pdf_bytes: bytes):
    result = parse_resume_document("sample.pdf", sample_pdf_bytes)
    assert result.filename == "sample.pdf"
    assert result.file_type == "pdf"
    assert "John Doe" in result.extracted_text
    assert result.character_count == len(result.extracted_text)
    assert result.page_count == 1


def test_parse_resume_document_docx(sample_docx_bytes: bytes):
    result = parse_resume_document("sample.docx", sample_docx_bytes)
    assert result.filename == "sample.docx"
    assert result.file_type == "docx"
    assert "Jane Smith" in result.extracted_text
    assert result.character_count == len(result.extracted_text)
    assert result.page_count is None
