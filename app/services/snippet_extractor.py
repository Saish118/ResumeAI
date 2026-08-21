"""Modular snippet extraction service for candidate resume text."""

import re
from typing import List, Optional

# Common resume section header patterns to filter out standalone header lines
SECTION_HEADER_PATTERN = re.compile(
    r"^(?:work\s+experience|professional\s+experience|experience|employment\s+history|"
    r"education|academic\s+background|technical\s+skills|skills|key\s+skills|summary|"
    r"professional\s+summary|profile|projects|key\s+projects|certifications|achievements|"
    r"contact|contact\s+info|languages|interests|honors|awards|references)$",
    re.IGNORECASE,
)

# Bullet point prefixes to clean up
BULLET_PREFIX_PATTERN = re.compile(
    r"^\s*(?:[\u2022\u2023\u25b6\u25c0\u25ba\u25c4\u25cf\u25cb\u25e6\u25aa\u25ab\u25fe\u25fd\*\-\+\▪\►\–\—]|\d+[\.\)]|[a-zA-Z][\.\)])\s*"
)


class SnippetExtractor:
    """Helper service for extracting candidate evidence snippets from raw resume text."""

    def __init__(
        self,
        min_length: int = 10,
        max_length: int = 350,
        min_words: int = 2,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.min_words = min_words

    def is_valid_snippet(self, text: str) -> bool:
        """
        Checks if a string snippet is valid, non-empty, and not just a section header.
        """
        if not text:
            return False

        cleaned = text.strip()
        if len(cleaned) < self.min_length:
            return False

        words = cleaned.split()
        if len(words) < self.min_words:
            return False

        # Filter out standalone section headers (e.g., "EXPERIENCE", "TECHNICAL SKILLS")
        if SECTION_HEADER_PATTERN.match(cleaned):
            return False

        # Filter out email-only or phone-only lines
        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", cleaned) or re.match(r"^\+?[\d\s\-\(\)]{7,20}$", cleaned):
            return False

        return True

    def clean_snippet(self, text: str) -> str:
        """
        Cleans leading bullets, numbers, and normalizes internal whitespace.
        """
        text = BULLET_PREFIX_PATTERN.sub("", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_snippets_from_text(self, text: Optional[str]) -> List[str]:
        """
        Splits raw resume text into concise, sentence-level or bullet-point evidence snippets.

        Args:
            text: Raw resume document text.

        Returns:
            List of clean, unique, order-preserved candidate resume snippets.
        """
        if not text or not text.strip():
            return []

        candidates: List[str] = []

        # 1. First split by newlines (bullet lines or line breaks)
        raw_lines = text.splitlines()

        for line in raw_lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Split line into individual sentences if it contains sentence boundaries
            sentences = re.split(r"(?<=[.!?])\s+", line_clean)
            if len(sentences) > 1:
                for sentence in sentences:
                    sentence_clean = self.clean_snippet(sentence)
                    if self.is_valid_snippet(sentence_clean):
                        candidates.append(sentence_clean)
            else:
                snippet = self.clean_snippet(line_clean)
                if self.is_valid_snippet(snippet):
                    candidates.append(snippet)

        # 2. De-duplicate while preserving appearance order
        seen_lower = set()
        unique_snippets: List[str] = []

        for snippet in candidates:
            lowered = snippet.lower()
            if lowered not in seen_lower:
                seen_lower.add(lowered)
                unique_snippets.append(snippet)

        return unique_snippets


# Global singleton instance
snippet_extractor = SnippetExtractor()
