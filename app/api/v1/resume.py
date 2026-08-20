"""Resume API endpoints for document upload and parsing."""

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.schemas.resume import (
    ResumeParseResponse,
    ExperienceExtractRequest,
    ExperienceExtractionResult,
)
from app.services.document_parser import (
    parse_resume_document,
    DocumentParsingError,
)
from app.services.document_validator import DocumentValidationError
from app.services.experience_extractor import experience_extractor

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post(
    "/parse",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and parse a resume document (PDF or DOCX)"
)
async def parse_resume(file: UploadFile = File(...)) -> ResumeParseResponse:
    """
    Accepts a resume upload (PDF or DOCX format), validates file format/integrity,
    extracts the raw text, and returns structured metadata including character and page count.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded or filename is missing."
        )

    try:
        content = await file.read()
        parsed_result = parse_resume_document(file.filename, content)
        return parsed_result
    except DocumentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except DocumentParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the document: {str(e)}"
        ) from e


@router.post(
    "/experience",
    response_model=ExperienceExtractionResult,
    status_code=status.HTTP_200_OK,
    summary="Extract candidate work experience from raw resume text"
)
def extract_experience(request: ExperienceExtractRequest) -> ExperienceExtractionResult:
    """
    Accepts raw resume text, parses work experience sections and date ranges,
    reconciles overlapping jobs, and returns total candidate experience years with evidence snippets.
    """
    if request.text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request text cannot be null."
        )

    try:
        result = experience_extractor.extract_experience(request.text)
        return ExperienceExtractionResult(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during experience extraction: {str(e)}"
        ) from e

