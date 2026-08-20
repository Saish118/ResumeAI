"""Resume parsing request/response schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ExperienceExtractRequest(BaseModel):
    """Request payload schema for experience extraction."""
    text: str = Field(..., description="Raw resume text string")


class ExperienceExtractionResult(BaseModel):
    """Structured response schema for extracted candidate work experience."""
    candidate_experience_years: Optional[float] = Field(
        default=None,
        description="Total extracted work experience in years"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Extracted evidence snippets for work experience"
    )
    confidence: str = Field(
        default="low",
        description="Confidence level of experience extraction ('high', 'medium', 'low')"
    )


class ResumeParseResponse(BaseModel):
    """Structured response schema for parsed resume document."""
    id: Optional[int] = Field(default=None, description="Database record ID if persisted")
    filename: str = Field(..., description="Original filename of the uploaded document")
    file_type: str = Field(..., description="Normalized document type extension ('pdf' or 'docx')")
    extracted_text: str = Field(..., description="Raw text extracted from the document")
    character_count: int = Field(..., description="Total character count of the extracted text")
    page_count: Optional[int] = Field(
        default=None,
        description="Total page count for PDF documents. Null for DOCX documents."
    )
    experience: Optional[ExperienceExtractionResult] = Field(
        default=None,
        description="Optional extracted candidate experience result"
    )

