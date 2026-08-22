"""Match Engine API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.schemas.match import MatchRequest, MatchResponse
from app.services.matching_engine import matching_engine
from app.db.database import get_db
from app.db.models import MatchAnalysis

router = APIRouter(tags=["Matching"])


@router.post(
    "/match",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare structured candidate resume against job requirements and generate explainable match analysis"
)
def match_resume_to_job(
    request: MatchRequest,
    db: Session = Depends(get_db)
) -> MatchResponse:
    """
    Accepts structured resume data and job requirements, performs exact skill matching,
    evaluates experience fit, computes requirement-level semantic evidence similarity,
    persists a MatchAnalysis record, and returns a structured match score (0 to 100) with explainability metrics.
    """
    if request.resume is None or request.job is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'resume' and 'job' objects must be provided in the request payload."
        )

    try:
        result = matching_engine.match(request)

        # Persist MatchAnalysis record
        try:
            semantic_list = [
                item.model_dump() if hasattr(item, "model_dump") else item.dict()
                for item in (result.semantic_evidence_matches or [])
            ]
            match_rec = MatchAnalysis(
                resume_analysis_id=request.resume_analysis_id,
                job_analysis_id=request.job_analysis_id,
                overall_score=result.overall_score,
                matched_required_skills=result.matched_required_skills or [],
                missing_required_skills=result.missing_required_skills or [],
                matched_preferred_skills=result.matched_preferred_skills or [],
                missing_preferred_skills=result.missing_preferred_skills or [],
                experience_status=result.experience_assessment.status if result.experience_assessment else "unknown",
                candidate_experience_years=result.experience_assessment.candidate_years if result.experience_assessment else None,
                required_experience_years=result.experience_assessment.required_years if result.experience_assessment else None,
                semantic_evidence_matches=semantic_list,
                summary=result.summary,
            )
            db.add(match_rec)
            db.commit()
            db.refresh(match_rec)

            result.id = match_rec.id
            result.resume_analysis_id = request.resume_analysis_id
            result.job_analysis_id = request.job_analysis_id
        except Exception:
            db.rollback()

        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        ) from ve
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during match computation: {str(e)}"
        ) from e


