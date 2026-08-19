"""Skill extraction API endpoints."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.skill import SkillExtractRequest, SkillExtractResponse
from app.services.skill_extractor import skill_extractor

router = APIRouter(prefix="/resume", tags=["Skills"])


@router.post(
    "/skills",
    response_model=SkillExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract skills from resume or job description text"
)
def extract_skills(request: SkillExtractRequest) -> SkillExtractResponse:
    """
    Accepts raw resume or job description text, normalizes tokens, matches explicit skills
    against a controlled taxonomy, deduplicates canonical skill outputs, and returns
    structured skill details with evidence snippets.
    """
    if request.text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request text cannot be null."
        )

    try:
        result = skill_extractor.extract_skills(request.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during skill extraction: {str(e)}"
        ) from e
