"""Modular rule and taxonomy-based skill extraction service."""

import re
from typing import Dict, List, Tuple, Optional
from app.core.taxonomy import SKILL_TAXONOMY
from app.schemas.skill import SkillDetail, SkillExtractResponse


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
        canonical_matches: Dict[str, Tuple[int, str, str, str]] = {}

        for category, canonical_name, alias, pattern in self._compiled_patterns:
            for match in pattern.finditer(text):
                start_pos, end_pos = match.span()
                matched_text = text[start_pos:end_pos]

                # Extract context snippet around match
                snippet_start = max(0, start_pos - 25)
                snippet_end = min(len(text), end_pos + 25)
                evidence = text[snippet_start:snippet_end].replace("\n", " ").strip()

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
