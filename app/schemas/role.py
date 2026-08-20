"""Pydantic schemas for ML Role Classification."""

from pydantic import BaseModel, Field


class RolePredictRequest(BaseModel):
    """Request payload for role classification."""
    text: str = Field(..., description="Raw text of candidate resume")


class RolePredictResponse(BaseModel):
    """Structured response payload containing predicted role and raw model score."""
    predicted_role: str = Field(..., description="Predicted job role category (one of 24 taxonomy categories)")
    confidence: float = Field(
        ...,
        description="Classifier raw probability/uncalibrated model score bounded between 0.0 and 1.0",
        ge=0.0,
        le=1.0
    )
