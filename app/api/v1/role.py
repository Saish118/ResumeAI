"""ML Role Classification API endpoints."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.role import RolePredictRequest, RolePredictResponse
from app.services.role_classifier import role_classifier

router = APIRouter(prefix="/role", tags=["Role Classification"])


@router.post(
    "/predict",
    response_model=RolePredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict job role category from candidate resume text using trained ML classifier"
)
def predict_role(request: RolePredictRequest) -> RolePredictResponse:
    """
    Accepts candidate resume text, processes tokens through the trained TF-IDF + Logistic Regression
    pipeline, and returns the predicted job category along with confidence score.
    """
    if request.text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request text cannot be null."
        )

    try:
        result = role_classifier.predict_role(request.text)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during role prediction: {str(e)}"
        ) from e
