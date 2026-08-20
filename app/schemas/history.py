"""Pydantic response schemas for history API endpoints."""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class ResumeAnalysisHistoryItem(BaseModel):
    """Structured response item for stored resume analysis history."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_type: str
    character_count: int
    page_count: Optional[int] = None
    extracted_text: Optional[str] = None
    predicted_role: Optional[str] = None
    role_model_score: Optional[float] = None
    candidate_experience_years: Optional[float] = None
    created_at: datetime


class JobAnalysisHistoryItem(BaseModel):
    """Structured response item for stored job description analysis history."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    minimum_experience_years: Optional[int] = None
    created_at: datetime


class MatchAnalysisHistoryItem(BaseModel):
    """Structured response summary item for stored match evaluation history."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_analysis_id: Optional[int] = None
    job_analysis_id: Optional[int] = None
    overall_score: float
    matched_required_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    experience_status: str
    candidate_experience_years: Optional[float] = None
    required_experience_years: Optional[int] = None
    summary: str
    created_at: datetime


class MatchAnalysisDetailResponse(BaseModel):
    """Detailed response model for single stored match analysis record with related resume/job info."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_analysis_id: Optional[int] = None
    job_analysis_id: Optional[int] = None
    overall_score: float
    matched_required_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    matched_preferred_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    experience_status: str
    candidate_experience_years: Optional[float] = None
    required_experience_years: Optional[int] = None
    semantic_evidence_matches: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str
    created_at: datetime

    # Related items
    resume_analysis: Optional[ResumeAnalysisHistoryItem] = None
    job_analysis: Optional[JobAnalysisHistoryItem] = None
