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


class ExperienceExtractor:
    """
    Extracts total candidate work experience in years, evidence snippets, and confidence levels
    from parsed resume text.
    """

    def __init__(self, current_year: Optional[int] = None, current_month: Optional[int] = None):
        now = datetime.now()
        self.current_year = current_year or now.year
        self.current_month = current_month or now.month

    def _extract_experience_section(self, text: str) -> str:
        """
        Extracts the Work Experience section from resume text if explicit section headers exist.
        If no section headers are found, returns the entire text.
        """
        lines = text.splitlines()
        exp_start_idx = None
        exp_end_idx = None

        section_header_pattern = re.compile(
            r'^\s*(?:work\s+experience|professional\s+experience|employment\s+history|work\s+history|experience|employment)\b',
            re.IGNORECASE
        )
        stop_header_pattern = re.compile(
            r'^\s*(?:education|projects|academic|certifications|skills|technical\s+skills|publications|awards|languages|references|summary|objective)\b',
            re.IGNORECASE
        )

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            if exp_start_idx is None:
                if section_header_pattern.match(stripped):
                    exp_start_idx = i
            else:
                if stop_header_pattern.match(stripped) and len(stripped.split()) <= 4:
                    exp_end_idx = i
                    break

        if exp_start_idx is not None:
            end_idx = exp_end_idx if exp_end_idx is not None else len(lines)
            return "\n".join(lines[exp_start_idx:end_idx])

        return text

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
        Extracts explicit summary statements of experience (e.g. '3+ years of experience', '5 years of work experience').
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
                    years = float(m.group(1))
                    # Ignore unreasonably large numbers (e.g., 50+ years) or 0
                    if 0.2 <= years <= 45.0:
                        return round(years, 1), [f"Explicit statement: \"{m.group(0)}\""]
                except ValueError:
                    continue

        return None, []

    def _extract_date_ranges(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts date ranges from text (e.g., 'Jan 2022 - Present', '01/2020 - 12/2022', '2019 - 2021').
        """
        month_pattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})'
        year_pattern = r'(?:19|20)\d{2}'
        present_pattern = r'(?:Present|Current|Now|Ongoing|Till\s+Date|Today)'

        # Pattern 1: Month Year - Month Year / Present (e.g. "Jan 2022 - Present", "01/2020 - 12/2022", "Feb 2021 to May 2023")
        range_pattern_1 = re.compile(
            rf'({month_pattern})\s*[\./-]?\s*({year_pattern})\s*(?:-|–|—|to)\s*(?:({month_pattern})\s*[\./-]?\s*({year_pattern})|({present_pattern}))',
            re.IGNORECASE
        )

        # Pattern 2: Year - Year / Present (e.g. "2019 - 2021", "2022 - Present")
        range_pattern_2 = re.compile(
            rf'\b({year_pattern})\s*(?:-|–|—|to)\s*(?:({year_pattern})|({present_pattern}))\b',
            re.IGNORECASE
        )

        ranges = []

        # Process Pattern 1
        for m in range_pattern_1.finditer(text):
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

            # Validate range integrity
            if e_year < s_year or (e_year == s_year and e_month < s_month):
                continue
            if s_year > self.current_year:
                continue

            snippet = text[max(0, m.start() - 40):min(len(text), m.end() + 40)].strip().replace('\n', ' ')
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

        # Process Pattern 2 (only if no Pattern 1 match covered this position)
        for m in range_pattern_2.finditer(text):

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
            if e_year < s_year:
                continue
            if s_year > self.current_year:
                continue

            snippet = text[max(0, m.start() - 40):min(len(text), m.end() + 40)].strip().replace('\n', ' ')

            # Check if overlapping with Pattern 1 range
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

        # Sort intervals by start month index
        intervals.sort(key=lambda x: x[0])

        merged = []
        for curr in intervals:
            if not merged:
                merged.append(curr)
            else:
                prev_start, prev_end, prev_r = merged[-1]
                curr_start, curr_end, curr_r = curr

                if curr_start <= prev_end + 1:
                    # Overlapping or contiguous interval -> merge
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

        # Step 1: Scope to work experience section if available
        exp_section_text = self._extract_experience_section(cleaned_text)

        # Step 2: Check for explicit experience summary statements (e.g. "3+ years of experience")
        explicit_years, explicit_evidence = self._extract_explicit_statements(cleaned_text)

        # Step 3: Extract employment date ranges from experience section
        date_ranges = self._extract_date_ranges(exp_section_text)
        if not date_ranges and exp_section_text != cleaned_text:
            # Fall back to full text if section isolation didn't yield dates
            date_ranges = self._extract_date_ranges(cleaned_text)

        # Step 4: Calculate duration & handle edge cases
        if date_ranges:
            total_months, range_evidence = self._merge_month_intervals(date_ranges)
            calculated_years = round(total_months / 12.0, 1)

            # Check if all ranges are internships
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

        # Step 5: Ambiguous / No Experience Found / Fresher -> Return null
        return {
            "candidate_experience_years": None,
            "evidence": [],
            "confidence": "low"
        }


# Singleton instance
experience_extractor = ExperienceExtractor()
