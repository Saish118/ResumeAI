"""History API endpoints for querying persisted analysis records."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ResumeAnalysis, JobAnalysis, MatchAnalysis
from app.schemas.history import (
    ResumeAnalysisHistoryItem,
    JobAnalysisHistoryItem,
    MatchAnalysisHistoryItem,
    MatchAnalysisDetailResponse,
)

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "/resumes",
    response_model=List[ResumeAnalysisHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get recent stored resume analysis history"
)
def get_resume_history(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[ResumeAnalysisHistoryItem]:
    """Retrieves recent resume analysis records ordered by created_at descending."""
    records = (
        db.query(ResumeAnalysis)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(limit)
        .all()
    )
    return records


@router.get(
    "/jobs",
    response_model=List[JobAnalysisHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get recent stored job description analysis history"
)
def get_job_history(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[JobAnalysisHistoryItem]:
    """Retrieves recent job description analysis records ordered by created_at descending."""
    records = (
        db.query(JobAnalysis)
        .order_by(JobAnalysis.created_at.desc())
        .limit(limit)
        .all()
    )
    return records


@router.get(
    "/matches",
    response_model=List[MatchAnalysisHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get recent stored resume ↔ job match evaluation history"
)
def get_match_history(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[MatchAnalysisHistoryItem]:
    """Retrieves recent match analysis records ordered by created_at descending."""
    records = (
        db.query(MatchAnalysis)
        .order_by(MatchAnalysis.created_at.desc())
        .limit(limit)
        .all()
    )
    return records


@router.get(
    "/matches/{match_id}",
    response_model=MatchAnalysisDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed stored match analysis record by ID"
)
def get_match_detail(
    match_id: int,
    db: Session = Depends(get_db)
) -> MatchAnalysisDetailResponse:
    """Retrieves one detailed match record by ID with related resume and job analysis data."""
    record = db.query(MatchAnalysis).filter(MatchAnalysis.id == match_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match record with ID {match_id} was not found."
        )
    return record
