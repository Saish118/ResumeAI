"""Modular rule and taxonomy-based skill extraction service."""

import re
from typing import Dict, List, Tuple, Optional
from app.core.taxonomy import SKILL_TAXONOMY
from app.schemas.skill import SkillDetail, SkillExtractResponse


BULLET_PREFIX_PATTERN = re.compile(
    r"^\s*(?:[\u2022\u2023\u25b6\u25c0\u25ba\u25c4\u25cf\u25cb\u25e6\u25aa\u25ab\u25fe\u25fd\*\-\+\▪\►\–\—]|\d+[\.\)]|[a-zA-Z][\.\)])\s*"
)


class SkillExtractor:
    """Taxonomy-based skill extractor with boundary-safe matching."""

    def __init__(self, taxonomy: Optional[Dict[str, Dict[str, List[str]]]] = None):
        self.taxonomy = taxonomy or SKILL_TAXONOMY
        self._compiled_patterns = self._build_compiled_patterns()

    def _build_compiled_patterns(self) -> List[Tuple[str, str, str, re.Pattern]]:
        """
        Pre-compiles boundary-safe regex patterns for all canonical skills and aliases.
        Returns a list of tuples: (category, canonical_name, alias, compiled_regex)
        """
        compiled = []
        for category, skills in self.taxonomy.items():
            for canonical_name, aliases in skills.items():
                all_aliases = set(aliases)
                all_aliases.add(canonical_name)

                # Sort aliases by length descending so longer phrases match first if overlapping
                sorted_aliases = sorted(all_aliases, key=lambda a: len(a), reverse=True)

                for alias in sorted_aliases:
                    normalized_alias = alias.strip().lower()
                    if not normalized_alias:
                        continue

                    escaped_alias = re.escape(normalized_alias)

                    # Determine trailing boundary based on last character of alias
                    if normalized_alias.endswith(("+", "#")):
                        trailing_boundary = r"(?![\w\+#])"
                    else:
                        # Prevent matching when followed by word char, +, #, or dot-word (e.g. react inside react.js)
                        trailing_boundary = r"(?![\w\+#]|\.\w)"

                    # Determine leading boundary based on first character of alias
                    if normalized_alias.startswith("."):
                        leading_boundary = r"(?<![\w\+#\-])"
                    else:
                        # Prevent matching when preceded by word char, +, #, ., or - (e.g. js inside react.js)
                        leading_boundary = r"(?<![\w\+#\.-])"

                    pattern_str = leading_boundary + escaped_alias + trailing_boundary
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    compiled.append((category, canonical_name, alias, pattern))
        return compiled

    def extract_skills(self, text: Optional[str]) -> SkillExtractResponse:
        """
        Extracts explicit skills from raw text based on controlled taxonomy.

        Args:
            text: Raw input text from resume or job description.

        Returns:
            SkillExtractResponse containing ordered canonical skills list and details.
        """
        if not text or not text.strip():
            return SkillExtractResponse(skills=[], extracted_skills=[])

        # Map canonical_skill -> best match info: (first_start_index, matched_alias, category, evidence)
    def _get_full_sentence_or_line(self, text: str, start_pos: int, end_pos: int) -> str:
        """
        Locates the full, untruncated sentence or bullet line in raw text containing the match position range.
        Ensures no arbitrary character window slicing occurs.
        """
        if not text:
            return ""

        # Find line boundaries around start_pos
        line_start = text.rfind("\n", 0, start_pos)
        line_start = 0 if line_start == -1 else line_start + 1

        line_end = text.find("\n", end_pos)
        line_end = len(text) if line_end == -1 else line_end

        line = text[line_start:line_end].strip()

        # Clean bullet prefix if present
        line_cleaned = BULLET_PREFIX_PATTERN.sub("", line).strip()
        line_cleaned = re.sub(r"\s+", " ", line_cleaned)

        # If line contains multiple sentences, locate sentence containing the matched alias
        sentences = re.split(r"(?<=[.!?])\s+", line_cleaned)
        if len(sentences) > 1:
            match_term = text[start_pos:end_pos].lower()
            for sentence in sentences:
                if match_term in sentence.lower():
                    return sentence.strip()

        return line_cleaned.strip()

    def extract_skills(self, text: Optional[str]) -> SkillExtractResponse:
        """
        Extracts explicit skills from raw text based on controlled taxonomy.

        Args:
            text: Raw input text from resume or job description.

        Returns:
            SkillExtractResponse containing ordered canonical skills list and details.
        """
        if not text or not text.strip():
            return SkillExtractResponse(skills=[], extracted_skills=[])

        # Map canonical_skill -> best match info: (first_start_index, matched_alias, category, evidence)
        canonical_matches: Dict[str, Tuple[int, str, str, str]] = {}

        for category, canonical_name, alias, pattern in self._compiled_patterns:
            for match in pattern.finditer(text):
                start_pos, end_pos = match.span()
                matched_text = text[start_pos:end_pos]

                # Extract full untruncated sentence or line evidence around match
                evidence = self._get_full_sentence_or_line(text, start_pos, end_pos)

                if canonical_name not in canonical_matches:
                    canonical_matches[canonical_name] = (start_pos, matched_text, category, evidence)
                else:
                    existing_start = canonical_matches[canonical_name][0]
                    # Update if this match occurs earlier in the document
                    if start_pos < existing_start:
                        canonical_matches[canonical_name] = (start_pos, matched_text, category, evidence)

        if not canonical_matches:
            return SkillExtractResponse(skills=[], extracted_skills=[])

        # Sort extracted skills by their first appearance order in the text
        sorted_canonical_items = sorted(
            canonical_matches.items(),
            key=lambda item: item[1][0]  # Sort by start_pos
        )

        canonical_skills_list = []
        detailed_skills_list = []

        for canonical_name, (start_pos, matched_alias, category, evidence) in sorted_canonical_items:
            canonical_skills_list.append(canonical_name)
            detailed_skills_list.append(
                SkillDetail(
                    skill=canonical_name,
                    matched_alias=matched_alias,
                    category=category,
                    evidence=evidence
                )
            )

        return SkillExtractResponse(
            skills=canonical_skills_list,
            extracted_skills=detailed_skills_list
        )


# Global singleton instance for reuse
skill_extractor = SkillExtractor()
