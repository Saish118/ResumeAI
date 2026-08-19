"""Match Engine API endpoints."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.match import MatchRequest, MatchResponse
from app.services.matching_engine import matching_engine

router = APIRouter(tags=["Matching"])


@router.post(
    "/match",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare structured candidate resume against job requirements and generate explainable match analysis"
)
def match_resume_to_job(request: MatchRequest) -> MatchResponse:
    """
    Accepts structured resume data and job requirements, performs exact skill matching,
    evaluates experience fit, computes requirement-level semantic evidence similarity,
    and returns a structured match score (0 to 100) with detailed explainability metrics.
    """
    if request.resume is None or request.job is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'resume' and 'job' objects must be provided in the request payload."
        )

    try:
        result = matching_engine.match(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during match computation: {str(e)}"
        ) from e
