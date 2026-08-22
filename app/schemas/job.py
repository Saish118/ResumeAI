"""Pydantic schemas for Job Description Processing."""

from typing import List, Optional
from pydantic import BaseModel, Field


class JobRequirementDetail(BaseModel):
    """Detailed skill requirement extracted from job description."""
    skill: str = Field(..., description="Name or canonical name of the skill")
    requirement_type: str = Field(..., description="Requirement classification: 'required' or 'preferred'")
    evidence: str = Field(..., description="Sentence or context snippet indicating the requirement")
    canonical_name: Optional[str] = Field(default=None, description="Canonical skill name if mapped to taxonomy")
    recognized_by_taxonomy: bool = Field(default=True, description="True if mapped to skill taxonomy, False if non-taxonomy requirement")



class JobProcessRequest(BaseModel):
    """Request payload for processing job description."""
    text: str = Field(..., description="Raw text of the job description")
    job_title: Optional[str] = Field(default=None, description="Optional job title")


class JobProcessResponse(BaseModel):
    """Structured response containing processed job requirements."""
    id: Optional[int] = Field(default=None, description="Database record ID if persisted")
    job_title: Optional[str] = Field(default=None, description="Job title if provided")
    required_skills: List[str] = Field(default_factory=list, description="List of required canonical skill names")
    preferred_skills: List[str] = Field(default_factory=list, description="List of preferred canonical skill names")
    minimum_experience_years: Optional[int] = Field(default=None, description="Extracted minimum years of experience")
    requirements: List[JobRequirementDetail] = Field(
        default_factory=list,
        description="Detailed requirements list for explainability and downstream matching"
    )
