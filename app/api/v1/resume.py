"""Resume API endpoints for document upload and parsing."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from sqlalchemy.orm import Session
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
from app.services.role_classifier import role_classifier
from app.services.resume_validator import resume_validator
from app.db.database import get_db
from app.db.models import ResumeAnalysis

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post(
    "/parse",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and parse a resume document (PDF or DOCX)"
)
async def parse_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> ResumeParseResponse:
    """
    Accepts a resume upload (PDF or DOCX format), validates file format/integrity,
    validates resume content structure, extracts raw text, predicts job role & candidate experience,
    persists a ResumeAnalysis record, and returns structured metadata.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded or filename is missing."
        )

    try:
        content = await file.read()
        parsed_result = parse_resume_document(file.filename, content)

        # Validate document content to ensure it is a valid resume
        validation_res = resume_validator.validate(parsed_result.extracted_text)
        if not validation_res["is_resume"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This document does not appear to be a resume. Please upload a resume containing information such as experience, education, skills, or projects."
            )

        # Run role classification & experience extraction for persistence record
        role_res = role_classifier.predict_role(parsed_result.extracted_text) if parsed_result.extracted_text else None
        exp_res = experience_extractor.extract_experience(parsed_result.extracted_text) if parsed_result.extracted_text else None

        # Persist ResumeAnalysis record
        try:
            resume_rec = ResumeAnalysis(
                filename=parsed_result.filename,
                file_type=parsed_result.file_type,
                character_count=parsed_result.character_count,
                page_count=parsed_result.page_count,
                extracted_text=parsed_result.extracted_text,
                predicted_role=role_res.predicted_role if role_res else None,
                role_model_score=role_res.confidence if role_res else None,
                candidate_experience_years=exp_res.get("candidate_experience_years") if exp_res else None,
            )
            db.add(resume_rec)
            db.commit()
            db.refresh(resume_rec)

            parsed_result.id = resume_rec.id
            if exp_res:
                parsed_result.experience = ExperienceExtractionResult(**exp_res)
        except Exception:
            db.rollback()

        return parsed_result
    except HTTPException:
        raise
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

