"""Document validation service for file extensions and content sanity."""

import os
from typing import Tuple

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


class DocumentValidationError(ValueError):
    """Custom exception raised when document validation fails."""
    pass


def validate_resume_file(filename: str, content: bytes) -> Tuple[str, str]:
    """
    Validates uploaded resume file.

    Args:
        filename: Name of the uploaded file.
        content: Raw byte content of the file.

    Returns:
        Tuple of (clean_filename, extension_without_dot) e.g. ("resume.pdf", "pdf")

    Raises:
        DocumentValidationError: If file extension is unsupported or content is empty.
    """
    if not filename:
        raise DocumentValidationError("Filename must not be empty.")

    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        supported_str = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise DocumentValidationError(
            f"Unsupported file format '{ext}'. Supported formats are: {supported_str}"
        )

    if not content or len(content) == 0:
        raise DocumentValidationError("Uploaded file is empty (0 bytes).")

    file_type = ext.lstrip(".")
    return filename, file_type
