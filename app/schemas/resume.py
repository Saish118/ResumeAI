"""Resume parsing request/response schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ResumeParseResponse(BaseModel):
    """Structured response schema for parsed resume document."""
    filename: str = Field(..., description="Original filename of the uploaded document")
    file_type: str = Field(..., description="Normalized document type extension ('pdf' or 'docx')")
    extracted_text: str = Field(..., description="Raw text extracted from the document")
    character_count: int = Field(..., description="Total character count of the extracted text")
    page_count: Optional[int] = Field(
        default=None,
        description="Total page count for PDF documents. Null for DOCX documents."
    )
