"""Modular Semantic Similarity service using Sentence Transformers."""

from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer, util

from app.schemas.similarity import SimilarityRequest, SimilarityResponse

MODEL_NAME = "all-MiniLM-L6-v2"


class SimilarityService:
    """Service for computing semantic cosine similarity between texts using embeddings."""

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    def get_model(self) -> SentenceTransformer:
        """
        Lazy-loads and caches the SentenceTransformer model instance.
        Ensures the model is loaded only once and reused across comparisons.
        """
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def compute_similarity(self, text_a: Optional[str], text_b: Optional[str]) -> SimilarityResponse:
        """
        Computes the cosine similarity score between two text inputs.

        Args:
            text_a: First text input.
            text_b: Second text input.

        Returns:
            SimilarityResponse with similarity_score and model_name.
        """
        # Handle empty, None, or whitespace-only inputs safely
        if not text_a or not text_a.strip() or not text_b or not text_b.strip():
            return SimilarityResponse(
                similarity_score=0.0,
                model_name=self.model_name
            )

        str_a = text_a.strip()
        str_b = text_b.strip()

        # Check for identical strings directly for deterministic max score
        if str_a == str_b:
            return SimilarityResponse(
                similarity_score=1.0,
                model_name=self.model_name
            )

        model = self.get_model()

        # Compute vector embeddings for both texts
        embeddings = model.encode([str_a, str_b], convert_to_tensor=True)

        # Compute cosine similarity between vector embeddings
        cosine_sim = util.cos_sim(embeddings[0], embeddings[1]).item()

        # Clamp result to valid range [0.0, 1.0] and round to 4 decimal places
        clamped_score = max(0.0, min(1.0, float(cosine_sim)))
        score_rounded = round(clamped_score, 4)

        return SimilarityResponse(
            similarity_score=score_rounded,
            model_name=self.model_name
        )


# Global singleton service instance
similarity_service = SimilarityService()
