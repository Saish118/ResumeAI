"""Job Description Processing API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.schemas.job import JobProcessRequest, JobProcessResponse
from app.services.job_processor import job_processor
from app.db.database import get_db
from app.db.models import JobAnalysis

router = APIRouter(prefix="/job-description", tags=["Job Description"])


@router.post(
    "/process",
    response_model=JobProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Process raw job description text into structured requirements"
)
def process_job_description(
    request: JobProcessRequest,
    db: Session = Depends(get_db)
) -> JobProcessResponse:
    """
    Accepts job description text and an optional job title, extracts skills using the shared taxonomy,
    classifies requirements into required vs. preferred, parses minimum experience years,
    persists a JobAnalysis record, and returns a structured JSON object.
    """
    if request.text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request text cannot be null."
        )

    try:
        result = job_processor.process_job_description(request)

        # Validate job description sufficiency
        is_valid, validation_msg = job_processor.validate_job_description(request.text, result)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_msg
            )

        # Persist JobAnalysis record
        try:
            job_rec = JobAnalysis(
                job_title=result.job_title,
                job_description=request.text,
                required_skills=result.required_skills or [],
                preferred_skills=result.preferred_skills or [],
                minimum_experience_years=result.minimum_experience_years,
            )
            db.add(job_rec)
            db.commit()
            db.refresh(job_rec)

            result.id = job_rec.id
        except Exception:
            db.rollback()

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the job description: {str(e)}"
        ) from e


