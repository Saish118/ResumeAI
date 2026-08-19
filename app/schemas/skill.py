"""Pydantic schemas for Skill Extraction requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SkillDetail(BaseModel):
    """Detailed information for a single extracted skill."""
    skill: str = Field(..., description="Canonical name of the skill")
    matched_alias: str = Field(..., description="Exact alias matched in the text")
    category: str = Field(..., description="Taxonomy category of the skill")
    evidence: str = Field(..., description="Context snippet showing the skill in raw text")


class SkillExtractRequest(BaseModel):
    """Request payload for skill extraction."""
    text: str = Field(..., description="Raw text from resume or job description")


class SkillExtractResponse(BaseModel):
    """Response payload containing extracted skills and metadata."""
    skills: List[str] = Field(
        ...,
        description="Deduplicated list of canonical skill names ordered by first appearance"
    )
    extracted_skills: List[SkillDetail] = Field(
        default_factory=list,
        description="Extensible list of detailed skill extractions including aliases, categories, and evidence"
    )
