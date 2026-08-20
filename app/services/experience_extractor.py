"""Candidate Work Experience Extraction Service."""

import re
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any


MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

PRESENT_TERMS = {"present", "current", "now", "ongoing", "till date", "today"}

WORK_EXP_HEADER_RE = re.compile(
    r'^\s*(?:work\s+experience|professional\s+experience|employment\s+history|work\s+history|career\s+history|relevant\s+experience|work\s+&\s+internship\s+experience|internship\s+experience|internships|experience|employment)\b',
    re.IGNORECASE
)

NON_WORK_HEADER_RE = re.compile(
    r'^\s*(?:education|academic\s+background|academic\s+profile|academic\s+qualifications|academics|qualifications|educational\s+background|projects|academic\s+projects|personal\s+projects|key\s+projects|certifications|certificates|licenses(?:\s+&\s+certifications)?|trainings?|training\s+&\s+workshops|workshops|skills|technical\s+skills|core\s+competencies|publications|awards|honors|achievements|extracurricular(?:\s+activities)?|activities|volunteering|volunteer\s+experience|languages|references|summary|profile|objective)\b',
    re.IGNORECASE
)

EDUCATION_KEYWORD_RE = re.compile(
    r'\b(?:university|college|polytechnic|institute|school|academy|degree|bachelor|b\.tech|b\.e\.|b\.s\.|b\.a\.|b\.c\.a\.|master|m\.tech|m\.e\.|m\.s\.|m\.c\.a\.|ph\.d|phd|diploma|hsc|ssc|high\s+school|matriculation|gpa|cgpa)\b',
    re.IGNORECASE
)

CERTIFICATION_KEYWORD_RE = re.compile(
    r'\b(?:certification|certificate|certified|license|licence)\b',
    re.IGNORECASE
)


class ExperienceExtractor:
    """
    Extracts total candidate work experience in years, evidence snippets, and confidence levels
    from parsed resume text, enforcing section isolation to exclude education, certifications, and projects.
    """

    def __init__(self, current_year: Optional[int] = None, current_month: Optional[int] = None):
        now = datetime.now()
        self.current_year = current_year or now.year
        self.current_month = current_month or now.month

    def _parse_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses resume text into structured sections categorized as WORK_EXPERIENCE, NON_WORK, or UNKNOWN.
        """
        lines = text.splitlines()
        sections = []
        current_header = "HEADER"
        current_type = "UNKNOWN"
        current_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_lines.append(line)
                continue

            words = stripped.split()
            if len(words) <= 5:
                if WORK_EXP_HEADER_RE.match(stripped):
                    if current_lines:
                        sections.append({
                            "header": current_header,
                            "type": current_type,
                            "text": "\n".join(current_lines)
                        })
                    current_header = stripped
                    current_type = "WORK_EXPERIENCE"
                    current_lines = []
                    continue
                elif NON_WORK_HEADER_RE.match(stripped):
                    if current_lines:
                        sections.append({
                            "header": current_header,
                            "type": current_type,
                            "text": "\n".join(current_lines)
                        })
                    current_header = stripped
                    current_type = "NON_WORK"
                    current_lines = []
                    continue

            current_lines.append(line)

        if current_lines:
            sections.append({
                "header": current_header,
                "type": current_type,
                "text": "\n".join(current_lines)
            })

        return sections

    def _parse_month_year(self, month_str: str, year_str: str) -> Tuple[int, int]:
        """Converts month string and year string into (year, month) tuple."""
        year = int(year_str)
        month_lower = month_str.lower().strip('. ') if month_str else ""

        if month_lower in MONTH_MAP:
            month = MONTH_MAP[month_lower]
        elif month_lower.isdigit():
            month = max(1, min(12, int(month_lower)))
        else:
            month = 1

        return year, month

    def _extract_explicit_statements(self, text: str) -> Tuple[Optional[float], List[str]]:
        """
        Extracts explicit summary statements of work experience (e.g. '3+ years of experience').
        Excludes snippets associated with education or certifications.
        """
        patterns = [
            r'(\b\d+(?:\.\d+)?)\s*\+\s*years?(?:\s+of)?\s+(?:professional|work|industry|overall|total|software|backend|frontend|data)?\s*experience',
            r'(\b\d+(?:\.\d+)?)\s*years?(?:\s+of)?\s+(?:professional|work|industry|overall|total|software|backend|frontend|data)?\s*experience',
            r'(?:over|more than|approx(?:imately)?|around|has)\s*(\d+(?:\.\d+)?)\s*\+?\s*years?(?:\s+of)?\s+experience',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for m in matches:
                try:
                    snippet = text[max(0, m.start() - 50):min(len(text), m.end() + 50)].strip().replace('\n', ' ')
                    if EDUCATION_KEYWORD_RE.search(snippet) or CERTIFICATION_KEYWORD_RE.search(snippet):
                        continue

                    years = float(m.group(1))
                    if 0.2 <= years <= 45.0:
                        return round(years, 1), [f"Explicit statement: \"{m.group(0)}\""]
                except ValueError:
                    continue

        return None, []

    def _extract_date_ranges(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts date ranges from text, filtering out snippets tied to education or certifications.
        """
        month_pattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})'
        year_pattern = r'(?:19|20)\d{2}'
        present_pattern = r'(?:Present|Current|Now|Ongoing|Till\s+Date|Today)'

        # Pattern 1: Month Year - Month Year / Present
        range_pattern_1 = re.compile(
            rf'({month_pattern})\s*[\./-]?\s*({year_pattern})\s*(?:-|–|—|to)\s*(?:({month_pattern})\s*[\./-]?\s*({year_pattern})|({present_pattern}))',
            re.IGNORECASE
        )

        # Pattern 2: Year - Year / Present
        range_pattern_2 = re.compile(
            rf'\b({year_pattern})\s*(?:-|–|—|to)\s*(?:({year_pattern})|({present_pattern}))\b',
            re.IGNORECASE
        )

        ranges = []

        # Process Pattern 1
        for m in range_pattern_1.finditer(text):
            snippet = text[max(0, m.start() - 60):min(len(text), m.end() + 60)].strip().replace('\n', ' ')

            # Skip ranges explicitly associated with education or certification terms
            if EDUCATION_KEYWORD_RE.search(snippet) or CERTIFICATION_KEYWORD_RE.search(snippet):
                continue

            start_m, start_y = m.group(1), m.group(2)
            end_m, end_y, end_pres = m.group(3), m.group(4), m.group(5)

            s_year, s_month = self._parse_month_year(start_m, start_y)

            if end_pres and end_pres.lower() in PRESENT_TERMS:
                e_year, e_month = self.current_year, self.current_month
                is_present = True
            elif end_y:
                e_year, e_month = self._parse_month_year(end_m, end_y)
                is_present = False
            else:
                continue

            if e_year < s_year or (e_year == s_year and e_month < s_month):
                continue
            if s_year > self.current_year:
                continue

            is_internship = bool(re.search(r'\bintern(?:ship)?\b', snippet, re.IGNORECASE))

            ranges.append({
                "start_year": s_year,
                "start_month": s_month,
                "end_year": e_year,
                "end_month": e_month,
                "is_present": is_present,
                "is_internship": is_internship,
                "match_text": m.group(0),
                "snippet": snippet
            })

        # Process Pattern 2
        for m in range_pattern_2.finditer(text):
            snippet = text[max(0, m.start() - 60):min(len(text), m.end() + 60)].strip().replace('\n', ' ')

            if EDUCATION_KEYWORD_RE.search(snippet) or CERTIFICATION_KEYWORD_RE.search(snippet):
                continue

            s_year = int(m.group(1))
            end_y, end_pres = m.group(2), m.group(3)

            if end_pres and end_pres.lower() in PRESENT_TERMS:
                e_year, e_month = self.current_year, self.current_month
                is_present = True
            elif end_y:
                e_year, e_month = int(end_y), 12
                is_present = False
            else:
                continue

            s_month = 1
            if e_year < s_year or s_year > self.current_year:
                continue

            if any(r["match_text"] in m.group(0) or m.group(0) in r["match_text"] for r in ranges):
                continue

            is_internship = bool(re.search(r'\bintern(?:ship)?\b', snippet, re.IGNORECASE))

            ranges.append({
                "start_year": s_year,
                "start_month": s_month,
                "end_year": e_year,
                "end_month": e_month,
                "is_present": is_present,
                "is_internship": is_internship,
                "match_text": m.group(0),
                "snippet": snippet
            })

        return ranges

    def _merge_month_intervals(self, ranges: List[Dict[str, Any]]) -> Tuple[int, List[str]]:
        """
        Converts date ranges into month index intervals, merges overlapping intervals,
        and returns total unique experience months and evidence snippets for each range.
        """
        if not ranges:
            return 0, []

        intervals = []
        evidence = []

        for r in ranges:
            start_idx = r["start_year"] * 12 + r["start_month"]
            end_idx = r["end_year"] * 12 + r["end_month"]
            intervals.append((start_idx, end_idx, r))

            months = max(1, end_idx - start_idx + 1)
            evidence.append(f"{r['match_text']}: {round(months / 12.0, 1)}y ({r['snippet']})")

        intervals.sort(key=lambda x: x[0])

        merged = []
        for curr in intervals:
            if not merged:
                merged.append(curr)
            else:
                prev_start, prev_end, prev_r = merged[-1]
                curr_start, curr_end, curr_r = curr

                if curr_start <= prev_end + 1:
                    new_end = max(prev_end, curr_end)
                    merged[-1] = (prev_start, new_end, prev_r)
                else:
                    merged.append(curr)

        total_months = 0
        for start_idx, end_idx, r in merged:
            months = max(1, end_idx - start_idx + 1)
            total_months += months

        return total_months, evidence

    def extract_experience(self, text: Optional[str]) -> Dict[str, Any]:
        """
        Main extraction entry point. Evaluates raw resume text and returns:
        {
            "candidate_experience_years": Optional[float],
            "evidence": List[str],
            "confidence": "high" | "medium" | "low"
        }
        """
        if not text or not text.strip():
            return {
                "candidate_experience_years": None,
                "evidence": [],
                "confidence": "low"
            }

        cleaned_text = text.strip()
        sections = self._parse_sections(cleaned_text)

        # Target WORK_EXPERIENCE sections if explicitly present
        work_sections = [s["text"] for s in sections if s["type"] == "WORK_EXPERIENCE"]
        if work_sections:
            target_text = "\n".join(work_sections)
        else:
            # If explicit NON_WORK sections (e.g. EDUCATION, PROJECTS) were found, exclude them
            has_non_work = any(s["type"] == "NON_WORK" for s in sections)
            if has_non_work:
                target_text = "\n".join([s["text"] for s in sections if s["type"] != "NON_WORK"])
            else:
                target_text = cleaned_text

        # Extract explicit summary statements and date ranges
        explicit_years, explicit_evidence = self._extract_explicit_statements(cleaned_text)
        date_ranges = self._extract_date_ranges(target_text)

        if date_ranges:
            total_months, range_evidence = self._merge_month_intervals(date_ranges)
            calculated_years = round(total_months / 12.0, 1)

            all_internships = all(r.get("is_internship", False) for r in date_ranges)

            if explicit_years is not None:
                final_years = max(explicit_years, calculated_years)
                combined_evidence = explicit_evidence + range_evidence
                confidence = "high"
            else:
                final_years = calculated_years
                combined_evidence = range_evidence
                confidence = "medium" if (all_internships or len(date_ranges) == 1) else "high"

            return {
                "candidate_experience_years": final_years,
                "evidence": combined_evidence,
                "confidence": confidence
            }

        elif explicit_years is not None:
            return {
                "candidate_experience_years": explicit_years,
                "evidence": explicit_evidence,
                "confidence": "medium"
            }

        return {
            "candidate_experience_years": None,
            "evidence": [],
            "confidence": "low"
        }


# Singleton instance
experience_extractor = ExperienceExtractor()
