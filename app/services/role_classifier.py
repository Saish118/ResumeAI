"""Modular ML Role Classification service loading serialized scikit-learn pipeline."""

import os
from typing import Optional, List
import joblib
from app.schemas.role import RolePredictRequest, RolePredictResponse

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "role_classifier.joblib"
)


class RoleClassifier:
    """Service for classifying candidate resumes into job categories using trained ML pipeline."""

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self._model = None

    def get_model(self):
        """
        Lazy-loads and caches the serialized scikit-learn pipeline model.
        Fails clearly if the model file does not exist.
        """
        if self._model is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(
                    f"Trained role classifier model artifact not found at '{self.model_path}'. "
                    "Please run 'python ml_training.py' to generate the model artifact."
                )
            self._model = joblib.load(self.model_path)
        return self._model

    @property
    def known_categories(self) -> List[str]:
        """Returns the list of 24 known category classes from the trained model."""
        model = self.get_model()
        classifier = model.named_steps.get("classifier")
        if classifier and hasattr(classifier, "classes_"):
            return list(classifier.classes_)
        return []

    def predict_role(self, text: Optional[str]) -> RolePredictResponse:
        """
        Predicts the job role category and uncalibrated raw model score for input text.

        Args:
            text: Raw input text from resume.

        Returns:
            RolePredictResponse containing predicted_role and raw model score (confidence field).
        """
        if not text or not text.strip():
            return RolePredictResponse(
                predicted_role="Unknown",
                confidence=0.0
            )

        clean_text = text.strip()
        model = self.get_model()

        # Predict class label
        predictions = model.predict([clean_text])
        predicted_role = str(predictions[0])

        # Compute raw model score from class probabilities (uncalibrated)
        confidence = 0.0
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba([clean_text])[0]
            max_prob = float(max(probabilities))
            confidence = round(max(0.0, min(1.0, max_prob)), 4)

        return RolePredictResponse(
            predicted_role=predicted_role,
            confidence=confidence
        )


# Global singleton instance
role_classifier = RoleClassifier()
