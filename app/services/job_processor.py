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
    "preferred skills",
    "preferred",
    "nice to have",
    "nice-to-have",
    "good to have",
    "would be a plus",
    "optional",
    "advantage",
    "desirable",
    "desired skills",
    "desired",
    "bonus",
    "plus",
]

REQUIRED_INDICATORS = [
    "required skills",
    "required",
    "must have",
    "must-have",
    "must",
    "mandatory skills",
    "mandatory",
    "essential",
    "minimum qualifications",
    "minimum",
    "should have",
    "at least",
    "need",
    "needs",
    "requirement",
    "requirements",
    "qualifications",
    "key skills",
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
        Classifies skill requirement as 'preferred' or 'required' based on sentence indicators and section context.
        """
        sentence_context = self._get_sentence_context(text, matched_alias, evidence)
        sentence_lower = sentence_context.lower()

        # 1. Explicit inline sentence indicators (if present in the sentence containing the skill)
        has_inline_preferred = any(indicator in sentence_lower for indicator in PREFERRED_INDICATORS)
        has_inline_required = any(indicator in sentence_lower for indicator in REQUIRED_INDICATORS)

        if has_inline_preferred and not has_inline_required:
            return "preferred"

        if has_inline_required and not has_inline_preferred:
            return "required"

        if has_inline_preferred and has_inline_required:
            alias_low = matched_alias.lower()
            alias_idx = sentence_lower.find(alias_low) if alias_low in sentence_lower else 0

            pref_dist = min((abs(sentence_lower.find(ind) - alias_idx) for ind in PREFERRED_INDICATORS if ind in sentence_lower), default=999)
            req_dist = min((abs(sentence_lower.find(ind) - alias_idx) for ind in REQUIRED_INDICATORS if ind in sentence_lower), default=999)

            if pref_dist < req_dist:
                return "preferred"
            elif req_dist < pref_dist:
                return "required"

        # 2. Section Context Fallback: Trace backward from line index in raw text to active section header
        if text:
            lines = text.splitlines()
            alias_lower = matched_alias.lower()
            evidence_clean = evidence.strip().lower() if evidence else ""

            matched_line_idx = -1
            for idx, line in enumerate(lines):
                line_low = line.strip().lower()
                if (evidence_clean and evidence_clean in line_low) or (alias_lower and alias_lower in line_low):
                    matched_line_idx = idx
                    break

            if matched_line_idx != -1:
                preferred_headers = [
                    "preferred skills", "preferred", "nice to have", "nice-to-have",
                    "good to have", "desired skills", "desired", "optional", "bonus",
                    "plus", "would be a plus", "advantage", "desirable"
                ]
                required_headers = [
                    "required skills", "required", "mandatory skills", "mandatory",
                    "must have", "must-have", "qualifications", "key skills",
                    "requirements", "responsibilities", "essential", "minimum qualifications"
                ]

                for idx in range(matched_line_idx, -1, -1):
                    header_line = lines[idx].strip().lower()
                    if not header_line:
                        continue

                    is_pref_sec = any(h in header_line for h in preferred_headers)
                    is_req_sec = any(h in header_line for h in required_headers)

                    if is_pref_sec and not is_req_sec:
                        return "preferred"
                    if is_req_sec and not is_pref_sec:
                        return "required"
                    if is_pref_sec and is_req_sec:
                        if header_line.startswith(("preferred", "nice to have", "good to have", "desired", "optional")):
                            return "preferred"
                        if header_line.startswith(("required", "must have", "qualifications", "key skills", "requirements")):
                            return "required"

        # 3. Default fallback
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
        seen_skills_lower = set()

        # 2. Classify each extracted skill requirement
        for detail in skill_extraction_result.extracted_skills:
            req_type = self.classify_requirement_type(text, detail.matched_alias, detail.evidence)
            sentence_evidence = self._get_sentence_context(text, detail.matched_alias, detail.evidence)
            seen_skills_lower.add(detail.skill.lower())

            if req_type == "preferred":
                if detail.skill not in preferred_skills:
                    preferred_skills.append(detail.skill)
                if detail.skill in required_skills:
                    required_skills.remove(detail.skill)
            else:
                if detail.skill not in preferred_skills and detail.skill not in required_skills:
                    required_skills.append(detail.skill)

            requirement_details.append(
                JobRequirementDetail(
                    skill=detail.skill,
                    requirement_type=req_type,
                    evidence=sentence_evidence,
                    canonical_name=detail.skill,
                    recognized_by_taxonomy=True,
                )
            )

        # 3. Extract structural job requirements not present in core skill taxonomy
        self._extract_non_taxonomy_requirements(
            text, seen_skills_lower, required_skills, preferred_skills, requirement_details
        )

        # 4. Extract minimum experience years
        min_experience = self.extract_minimum_experience(text)

        return JobProcessResponse(
            job_title=request.job_title,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            minimum_experience_years=min_experience,
            requirements=requirement_details
        )

    def _extract_non_taxonomy_requirements(
        self,
        text: str,
        seen_skills_lower: set,
        required_skills: List[str],
        preferred_skills: List[str],
        requirement_details: List[JobRequirementDetail],
    ) -> None:
        """
        Extracts explicit job requirements from structural bullet points, list items, and sections
        that are not recognized in the core technical skill taxonomy.
        """
        lines = text.splitlines()
        current_section_type = "required"

        noise_phrases = {
            "minimum experience", "years of experience", "years experience", "yr exp", "yrs exp",
            "equal opportunity", "competitive salary", "full time", "part time", "apply now",
            "job title", "benefits include", "about the company", "join our team", "we are hiring",
            "location", "work location", "hybrid", "remote", "onsite", "office", "qualifications",
            "requirements", "responsibilities", "preferred", "nice to have"
        }

        for raw_line in lines:
            line_str = raw_line.strip()
            if not line_str:
                continue

            line_lower = line_str.lower()

            # Track section header context changes
            if any(k in line_lower for k in ["preferred", "nice to have", "bonus", "plus", "good to have", "optional", "desired"]):
                current_section_type = "preferred"
            elif any(k in line_lower for k in ["required", "must have", "qualifications", "key skills", "requirements", "mandatory"]):
                current_section_type = "required"

            # Identify structural bullets, list items, or explicit requirement prefix lines
            is_req_prefix = bool(re.match(r"^(?:required|preferred|requirements|qualifications|skills|nice to have|must have)\s*:", line_str, re.IGNORECASE))
            is_bullet = bool(re.match(r"^(?:[•\*\-\+]|\d+[\.\)])\s+", line_str)) or line_str.startswith(("-", "•", "*", "+"))
            is_colon_header = line_str.endswith(":")

            if is_colon_header or not (is_bullet or is_req_prefix):
                continue

            # Strip leading bullet indicators and section prefixes
            cleaned_line = re.sub(r"^(?:[•\*\-\+\d+\.\s\[\]]+)", "", line_str).strip()
            cleaned_line = re.sub(
                r"^(?:required|preferred|requirements|qualifications|skills|nice to have|must have)\s*:\s*",
                "",
                cleaned_line,
                flags=re.IGNORECASE,
            ).strip()

            if not cleaned_line or len(cleaned_line) < 2:
                continue

            # Split comma, semicolon, or 'and' separated items if line is concise
            if len(cleaned_line) < 100:
                raw_candidates = [c.strip() for c in re.split(r"[,;]|\band\b", cleaned_line, flags=re.IGNORECASE) if c.strip()]
            else:
                raw_candidates = [cleaned_line]

            for candidate in raw_candidates:
                cand_clean = re.sub(r"^(?:[•\*\-\+\d+\.\s]+)", "", candidate).strip()
                cand_clean = cand_clean.rstrip(".")
                cand_lower = cand_clean.lower()

                if not cand_clean or len(cand_clean) < 2 or len(cand_clean) > 60:
                    continue

                # Skip noise phrases or experience patterns
                if cand_lower in noise_phrases:
                    continue
                if re.search(r"\b\d+\+?\s*(?:years?|yrs?)\b", cand_lower):
                    continue
                if cand_lower.startswith(("job title", "minimum experience", "experience:", "years")):
                    continue

                # Skip if already captured (case-insensitive check)
                if cand_lower in seen_skills_lower:
                    continue

                seen_skills_lower.add(cand_lower)

                # Classify requirement type
                req_type = self.classify_requirement_type(text, cand_clean, line_str)
                if current_section_type == "preferred" and not any(k in cand_clean.lower() for k in ["required", "must have", "mandatory"]):
                    req_type = "preferred"

                if req_type == "preferred":
                    if cand_clean not in preferred_skills:
                        preferred_skills.append(cand_clean)
                    if cand_clean in required_skills:
                        required_skills.remove(cand_clean)
                else:
                    if cand_clean not in preferred_skills and cand_clean not in required_skills:
                        required_skills.append(cand_clean)

                requirement_details.append(
                    JobRequirementDetail(
                        skill=cand_clean,
                        requirement_type=req_type,
                        evidence=line_str,
                        canonical_name=None,
                        recognized_by_taxonomy=False,
                    )
                )



    def validate_job_description(
        self, text: Optional[str], response: Optional[JobProcessResponse] = None
    ) -> Tuple[bool, str]:
        """
        Validates whether a job description contains meaningful evaluable requirements
        (e.g., required/preferred skills, experience requirements, responsibilities, or qualifications).

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        INSUFFICIENT_MSG = (
            "Insufficient job description. Please provide meaningful requirements, "
            "skills, responsibilities, or experience criteria to calculate a match score."
        )

        if not text or not text.strip():
            return False, INSUFFICIENT_MSG

        cleaned_text = text.strip()

        # If processed response provided, check extracted skills and minimum experience first
        if response is not None:
            if response.required_skills and len(response.required_skills) > 0:
                return True, "Valid job description."
            if response.preferred_skills and len(response.preferred_skills) > 0:
                return True, "Valid job description."
            if response.minimum_experience_years is not None:
                return True, "Valid job description."

        # Check explicit experience requirements in text
        exp_pattern = re.compile(
            r"\b(?:\d+\+?\s*(?:years?|yrs?)|experience\s+required|required\s+experience|"
            r"prior\s+experience|work\s+experience|entry\s+level|senior\s+level|years\s+of\s+experience)\b",
            re.IGNORECASE,
        )
        if exp_pattern.search(cleaned_text):
            return True, "Valid job description."

        # Check responsibilities, duties, tasks, or substantive action verbs/work items in text
        resp_pattern = re.compile(
            r"\b(?:responsibilities|responsibility|duties|essential\s+functions|what\s+you\s+will\s+do|"
            r"what\s+you\'ll\s+do|day\s+to\s+day|day-to-day|role\s+description|key\s+tasks|job\s+scope|deliverables|"
            r"designing|developing|implementing|building|maintaining|writing\s+code|unit\s+tests?|code\s+reviews?|"
            r"architecting|troubleshooting|deploying|monitoring|collaborating|managing|leading)\b",
            re.IGNORECASE,
        )
        if resp_pattern.search(cleaned_text):
            return True, "Valid job description."

        # Check qualifications / education requirements in text
        qual_pattern = re.compile(
            r"\b(?:qualifications|qualification|education|bachelor|master|phd|\bbs\b|\bms\b|"
            r"computer\s+science|degree|certification|certified)\b",
            re.IGNORECASE,
        )
        if qual_pattern.search(cleaned_text):
            return True, "Valid job description."

        return False, INSUFFICIENT_MSG


# Global singleton instance
job_processor = JobProcessor()

