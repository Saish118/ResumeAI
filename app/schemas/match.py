"""Pydantic schemas for Resume ↔ Job Matching Engine."""

from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.job import JobRequirementDetail
from app.schemas.skill import SkillDetail


class ResumeDataInput(BaseModel):
    """Structured candidate resume data input for matching."""
    skills: List[str] = Field(default_factory=list, description="Canonical list of candidate skills")
    extracted_skills: List[SkillDetail] = Field(
        default_factory=list,
        description="Detailed extracted skills with evidence snippets"
    )
    candidate_experience_years: Optional[int] = Field(
        default=None,
        description="Total years of candidate experience if available"
    )


class JobDataInput(BaseModel):
    """Structured job requirement data input for matching."""
    job_title: Optional[str] = Field(default=None, description="Job title")
    required_skills: List[str] = Field(default_factory=list, description="List of required canonical skill names")
    preferred_skills: List[str] = Field(default_factory=list, description="List of preferred canonical skill names")
    minimum_experience_years: Optional[int] = Field(
        default=None,
        description="Minimum required years of experience"
    )
    requirements: List[JobRequirementDetail] = Field(
        default_factory=list,
        description="Detailed job requirement items with evidence"
    )


class MatchRequest(BaseModel):
    """Request payload for matching structured resume data against job data."""
    resume: ResumeDataInput = Field(..., description="Candidate resume structured data")
    job: JobDataInput = Field(..., description="Job requirements structured data")


class ExperienceAssessment(BaseModel):
    """Assessment of candidate experience against job requirements."""
    required_years: Optional[int] = Field(default=None, description="Required minimum years of experience")
    candidate_years: Optional[int] = Field(default=None, description="Candidate years of experience")
    meets_requirement: Optional[bool] = Field(
        default=None,
        description="True if candidate meets or exceeds required years, False if below, None if unknown"
    )
    status: str = Field(..., description="Experience status: 'matched', 'below_requirement', or 'unknown'")


class SemanticEvidenceMatch(BaseModel):
    """Requirement-level semantic similarity match detail."""
    requirement_skill: str = Field(..., description="Skill associated with the job requirement")
    requirement_evidence: str = Field(..., description="Job requirement sentence text")
    best_matching_resume_evidence: Optional[str] = Field(
        default=None,
        description="Best matching resume evidence snippet if found"
    )
    similarity_score: float = Field(
        ...,
        description="Semantic similarity score between requirement and resume evidence (0.0 to 1.0)"
    )


class MatchResponse(BaseModel):
    """Structured response containing explainable match analysis and overall score."""
    overall_score: float = Field(
        ...,
        description="Overall match score bounded between 0.0 and 100.0",
        ge=0.0,
        le=100.0
    )
    matched_required_skills: List[str] = Field(default_factory=list, description="Required skills matched in resume")
    missing_required_skills: List[str] = Field(default_factory=list, description="Required skills missing from resume")
    matched_preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills matched in resume")
    missing_preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills missing from resume")
    experience_assessment: ExperienceAssessment = Field(..., description="Experience fit evaluation")
    semantic_evidence_matches: List[SemanticEvidenceMatch] = Field(
        default_factory=list,
        description="Requirement-level semantic evidence comparison results"
    )
    summary: str = Field(..., description="Human-readable plain language match summary")
