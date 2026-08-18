"""Resume API endpoints for document upload and parsing."""

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.schemas.resume import ResumeParseResponse
from app.services.document_parser import (
    parse_resume_document,
    DocumentParsingError,
)
from app.services.document_validator import DocumentValidationError

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
