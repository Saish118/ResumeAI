"""Modular Job Description Processing service."""

import re
from typing import List, Optional, Tuple
from app.schemas.job import (
    JobProcessRequest,
    JobProcessResponse,
    JobRequirementDetail,
)
from app.services.skill_extractor import skill_extractor, SkillExtractor

PREFERRED_INDICATORS = [
    "preferred",
    "nice to have",
    "bonus",
    "plus",
    "good to have",
    "would be a plus",
    "optional",
    "advantage",
    "desirable",
]

REQUIRED_INDICATORS = [
    "required",
    "must have",
    "must",
    "mandatory",
    "essential",
    "minimum",
    "should have",
    "at least",
    "need",
    "needs",
    "requirement",
    "requirements",
]

# Patterns for extracting minimum years of experience
EXPERIENCE_PATTERNS = [
    re.compile(r"minimum\s*(?:of\s*)?(\d+)\s*(?:[+\-]\d+)?\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"at\s*least\s*(\d+)\s*(?:[+\-]\d+)?\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"(\d+)\s*-\s*\d+\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*(?:years?|yrs?)", re.IGNORECASE),
]


class JobProcessor:
    """Service for processing job descriptions into structured requirements."""

    def __init__(self, extractor: Optional[SkillExtractor] = None):
        self.extractor = extractor or skill_extractor

    def extract_minimum_experience(self, text: str) -> Optional[int]:
        """
        Extracts the minimum required years of experience from job text.

        Args:
            text: Raw job description text.

        Returns:
            Minimum years as integer, or None if no experience mentioned.
        """
        if not text:
            return None

        found_years: List[int] = []

        for pattern in EXPERIENCE_PATTERNS:
            for match in pattern.finditer(text):
                try:
                    val = int(match.group(1))
                    # Sanity check: filter out unreasonable numbers like 2026 or 100
                    if 0 < val <= 30:
                        found_years.append(val)
                except (ValueError, IndexError):
                    continue

        if not found_years:
            return None

        return min(found_years)

    def _get_sentence_context(self, text: str, matched_alias: str, evidence: str) -> str:
        """
        Locates the specific sentence in raw text containing the matched skill alias.
        """
        if not text:
            return evidence

        sentences = re.split(r"(?<=[.!?\n])\s+", text)
        matched_alias_lower = matched_alias.lower()

        for sentence in sentences:
            if matched_alias_lower in sentence.lower():
                return sentence.strip()

        return evidence.strip()

    def classify_requirement_type(self, text: str, matched_alias: str, evidence: str) -> str:
        """
        Classifies skill requirement as 'preferred' or 'required' based on sentence context indicators.
        """
        sentence_context = self._get_sentence_context(text, matched_alias, evidence).lower()

        # Check preferred indicators first
        for indicator in PREFERRED_INDICATORS:
            if indicator in sentence_context:
                return "preferred"

        # Check required indicators
        for indicator in REQUIRED_INDICATORS:
            if indicator in sentence_context:
                return "required"

        # Default fallback when no explicit indicator is found
        return "required"

    def process_job_description(self, request: JobProcessRequest) -> JobProcessResponse:
        """
        Processes a raw job description into structured skill requirements and experience.

        Args:
            request: JobProcessRequest object.

        Returns:
            JobProcessResponse containing structured details.
        """
        text = request.text
        if not text or not text.strip():
            return JobProcessResponse(
                job_title=request.job_title,
                required_skills=[],
                preferred_skills=[],
                minimum_experience_years=None,
                requirements=[]
            )

        # 1. Extract skills using existing SkillExtractor service
        skill_extraction_result = self.extractor.extract_skills(text)

        required_skills: List[str] = []
        preferred_skills: List[str] = []
        requirement_details: List[JobRequirementDetail] = []

        # 2. Classify each extracted skill requirement
        for detail in skill_extraction_result.extracted_skills:
            req_type = self.classify_requirement_type(text, detail.matched_alias, detail.evidence)
            sentence_evidence = self._get_sentence_context(text, detail.matched_alias, detail.evidence)

            if req_type == "preferred":
                if detail.skill not in preferred_skills:
                    preferred_skills.append(detail.skill)
            else:
                if detail.skill not in required_skills:
                    required_skills.append(detail.skill)

            requirement_details.append(
                JobRequirementDetail(
                    skill=detail.skill,
                    requirement_type=req_type,
                    evidence=sentence_evidence
                )
            )

        # 3. Extract minimum experience years
        min_experience = self.extract_minimum_experience(text)

        return JobProcessResponse(
            job_title=request.job_title,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            minimum_experience_years=min_experience,
            requirements=requirement_details
        )


# Global singleton instance
job_processor = JobProcessor()
