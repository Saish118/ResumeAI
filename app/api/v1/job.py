"""Job Description Processing API endpoints."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.job import JobProcessRequest, JobProcessResponse
from app.services.job_processor import job_processor

router = APIRouter(prefix="/job-description", tags=["Job Description"])


@router.post(
    "/process",
    response_model=JobProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Process raw job description text into structured requirements"
)
def process_job_description(request: JobProcessRequest) -> JobProcessResponse:
    """
    Accepts job description text and an optional job title, extracts skills using the shared taxonomy,
    classifies requirements into required vs. preferred, parses minimum experience years,
    and returns a structured JSON object.
    """
    if request.text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request text cannot be null."
        )

    try:
        result = job_processor.process_job_description(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the job description: {str(e)}"
        ) from e
