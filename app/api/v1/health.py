"""Health check endpoint router."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check() -> HealthCheckResponse:
    """Return operational status of the service."""
    return HealthCheckResponse(
        status="healthy",
        service="ResumeAI Backend",
        version="0.1.0"
    )
