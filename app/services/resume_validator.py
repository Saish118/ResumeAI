"""Resume Content Validation Service."""

import re
from typing import Dict, Any, List, Tuple

RESUME_SECTIONS: List[Tuple[str, str, float]] = [
    (r'\b(?:work\s+experience|professional\s+experience|employment\s+history|work\s+history|career\s+history|experience|employment)\b', 'Experience Section', 0.30),
    (r'\b(?:education|academic\s+background|academic\s+profile|educational\s+background|academics|qualifications)\b', 'Education Section', 0.25),
    (r'\b(?:skills|technical\s+skills|core\s+competencies|programming\s+languages)\b', 'Skills Section', 0.25),
    (r'\b(?:projects|technical\s+projects|personal\s+projects|key\s+projects)\b', 'Projects Section', 0.20),
    (r'\b(?:certifications|certificates|licenses)\b', 'Certifications Section', 0.15),
    (r'\b(?:summary|professional\s+summary|profile|objective|career\s+objective)\b', 'Summary Section', 0.15),
]

CONTACT_PATTERNS: List[Tuple[str, str, float]] = [
    (r'[\w\.-]+@[\w\.-]+\.\w+', 'Email Address', 0.20),
    (r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', 'Phone Number', 0.15),
    (r'\b(?:linkedin\.com|github\.com|netlify\.app|vercel\.app|github\.io)\b', 'Portfolio / Profile Link', 0.15),
    (r'\b(?:resume|curriculum\s+vitae|\bcv\b)\b', 'Resume Header Keyword', 0.20),
]

NON_RESUME_PATTERNS: List[Tuple[str, str, float]] = [
    (r'\b(?:invoice|tax\s+invoice|bill\s+to|ship\s+to|amount\s+due|total\s+amount|invoice\s+number|invoice\s+date|payment\s+terms)\b', 'Invoice / Bill Document', 0.60),
    (r'\b(?:lab\s+report|laboratory\s+report|experiment\s+(?:no|number)|problem\s+statement|assignment\s+\d+|submitted\s+to|course\s+code|instructor:)\b', 'Academic Lab Report / Assignment', 0.50),
    (r'\b(?:abstract|introduction|related\s+work|methodology|experimental\s+results|ieee\s+transactions|arxiv|doi:)\b', 'Academic Research Paper', 0.50),
    (r'\b(?:statement\s+of\s+account|account\s+balance|opening\s+balance|closing_balance|transaction\s+history|debit|credit)\b', 'Financial Account Statement', 0.60),
    (r'\b(?:syllabus|course\s+outline|prerequisites|lecture\s+schedule|grading\s+policy)\b', 'Course Syllabus', 0.50),
]


class ResumeValidator:
    """
    Validates whether raw extracted text reasonably resembles a resume document using
    section headers, contact patterns, and non-resume document indicators.
    """

    def validate(self, text: str) -> Dict[str, Any]:
        """
        Evaluates input text and returns structured validation status:
        {
            "is_resume": bool,
            "score": float (0.0 to 1.0),
            "evidence": List[str],
            "reason": str
        }
        """
        if not text or not text.strip():
            return {
                "is_resume": False,
                "score": 0.0,
                "evidence": [],
                "reason": "Document contains no readable text."
            }

        cleaned = text.strip()
        positive_score = 0.0
        negative_score = 0.0
        evidence: List[str] = []

        # 1. Check positive resume section headers
        for pattern, name, weight in RESUME_SECTIONS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                positive_score += weight
                evidence.append(f"+ Found {name}")

        # 2. Check contact information & resume keywords
        for pattern, name, weight in CONTACT_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                positive_score += weight
                evidence.append(f"+ Found {name}")

        # 3. Check for employment / education date ranges
        date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})?[\./-]?\s*(?:19|20)\d{2}\s*(?:-|–|—|to)\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})?[\./-]?\s*(?:(?:19|20)\d{2}|Present|Current|Now)\b'
        if re.search(date_pattern, cleaned, re.IGNORECASE):
            positive_score += 0.15
            evidence.append("+ Found Employment / Education Date Ranges")

        # 4. Check negative non-resume signals
        for pattern, name, weight in NON_RESUME_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                negative_score += weight
                evidence.append(f"- Detected {name}")

        # 5. Calculate net validation score & decision
        net_score = max(0.0, positive_score - negative_score)
        final_score = round(min(1.0, net_score), 2)

        # Requires a minimum positive structural score and no strong non-resume penalty
        is_resume = (positive_score >= 0.25) and (negative_score < 0.50) and (final_score >= 0.25)

        if is_resume:
            reason = "Document validated as a resume."
        elif negative_score >= 0.50:
            reason = "Document contains strong non-resume indicators (e.g. invoice, lab report, paper, or statement)."
        else:
            reason = "Document lacks essential resume sections (e.g. experience, education, skills, or contact info)."

        return {
            "is_resume": is_resume,
            "score": final_score,
            "evidence": evidence,
            "reason": reason
        }


# Global singleton instance
resume_validator = ResumeValidator()
