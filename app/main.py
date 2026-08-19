"""Main entry point for the ResumeAI FastAPI Application."""

from fastapi import FastAPI
from app.api.v1.health import router as health_router
from app.api.v1.resume import router as resume_router
from app.api.v1.skill import router as skill_router
from app.api.v1.job import router as job_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# Root level health endpoint for convenience
@app.get("/health", include_in_schema=True, tags=["Health"])
def root_health():
    """Root health check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}

# Include API v1 routes
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(resume_router, prefix=settings.API_V1_STR)
app.include_router(skill_router, prefix=settings.API_V1_STR)
app.include_router(job_router, prefix=settings.API_V1_STR)
