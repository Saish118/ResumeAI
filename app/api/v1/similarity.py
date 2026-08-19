"""Semantic Similarity API endpoints."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.similarity import SimilarityRequest, SimilarityResponse
from app.services.similarity_service import similarity_service

router = APIRouter(tags=["Semantic Similarity"])


@router.post(
    "/similarity",
    response_model=SimilarityResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate semantic similarity score between two texts using Sentence Transformers"
)
def compute_similarity(request: SimilarityRequest) -> SimilarityResponse:
    """
    Accepts two text strings (`text_a` and `text_b`), converts them into sentence embeddings
    using the `all-MiniLM-L6-v2` model, calculates cosine similarity, and returns a normalized score.
    """
    if request.text_a is None or request.text_b is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="text_a and text_b cannot be null."
        )

    try:
        result = similarity_service.compute_similarity(request.text_a, request.text_b)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while computing similarity: {str(e)}"
        ) from e
