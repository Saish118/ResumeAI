"""Pydantic schemas for Semantic Similarity Service."""

from pydantic import BaseModel, Field


class SimilarityRequest(BaseModel):
    """Request payload for semantic similarity calculation."""
    text_a: str = Field(..., description="First text string to compare")
    text_b: str = Field(..., description="Second text string to compare")


class SimilarityResponse(BaseModel):
    """Structured response payload containing cosine similarity score."""
    similarity_score: float = Field(
        ...,
        description="Cosine similarity score normalized between 0.0 and 1.0",
        ge=0.0,
        le=1.0
    )
    model_name: str = Field(
        ...,
        description="Name of the Sentence Transformer model used"
    )
