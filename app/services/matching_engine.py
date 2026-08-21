"""Modular Resume ↔ Job Matching Engine Service v1."""

from typing import List, Optional, Tuple
from app.schemas.match import (
    MatchRequest,
    MatchResponse,
    ExperienceAssessment,
    SemanticEvidenceMatch,
)
from app.services.similarity_service import similarity_service, SimilarityService
from app.services.snippet_extractor import snippet_extractor, SnippetExtractor

DEFAULT_SIMILARITY_THRESHOLD = 0.35


class MatchingEngine:
    """
    Configurable, explainable matching engine that evaluates candidate resume data
    against job requirements using exact skill matching, experience assessment,
    and requirement-level semantic evidence comparison.
    """

    def __init__(
        self,
        similarity_svc: Optional[SimilarityService] = None,
        snippet_ext: Optional[SnippetExtractor] = None,
        weight_required_skills: float = 0.50,
        weight_preferred_skills: float = 0.20,
        weight_semantic_evidence: float = 0.20,
        weight_experience: float = 0.10,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        self.similarity_svc = similarity_svc or similarity_service
        self.snippet_extractor = snippet_ext or snippet_extractor
        self.w_required = weight_required_skills
        self.w_preferred = weight_preferred_skills
        self.w_semantic = weight_semantic_evidence
        self.w_experience = weight_experience
        self.similarity_threshold = similarity_threshold

    def evaluate_exact_skills(
        self, candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """
        Calculates exact canonical skill matches and missing skill lists for required and preferred skills.
        """
        cand_set = set(candidate_skills)

        matched_req = [s for s in required_skills if s in cand_set]
        missing_req = [s for s in required_skills if s not in cand_set]

        matched_pref = [s for s in preferred_skills if s in cand_set]
        missing_pref = [s for s in preferred_skills if s not in cand_set]

        return matched_req, missing_req, matched_pref, missing_pref

    def evaluate_experience(
        self, candidate_years: Optional[float], required_years: Optional[int]
    ) -> Tuple[ExperienceAssessment, float, bool]:
        """
        Assesses experience fit and returns ExperienceAssessment, sub-score (0-100), and boolean flag if active.
        """
        if required_years is None or candidate_years is None:
            assessment = ExperienceAssessment(
                required_years=required_years,
                candidate_years=candidate_years,
                meets_requirement=None,
                status="unknown",
            )
            return assessment, 100.0, False

        meets = candidate_years >= required_years
        status = "matched" if meets else "below_requirement"

        if meets:
            score = 100.0
        else:
            score = max(0.0, (candidate_years / required_years) * 100.0) if required_years > 0 else 0.0

        assessment = ExperienceAssessment(
            required_years=required_years,
            candidate_years=candidate_years,
            meets_requirement=meets,
            status=status,
        )
        return assessment, score, True

    def extract_candidate_snippets(self, match_request: MatchRequest) -> List[str]:
        """
        Extracts clean, distinct candidate resume snippets from raw text and extracted skill details.
        """
        snippets: List[str] = []
        seen_lower = set()

        # 1. Extract snippets from raw resume text if available
        if match_request.resume.raw_text:
            text_snippets = self.snippet_extractor.extract_snippets_from_text(match_request.resume.raw_text)
            for snip in text_snippets:
                low = snip.lower()
                if low not in seen_lower:
                    seen_lower.add(low)
                    snippets.append(snip)

        # 2. Extract snippets from extracted skill details evidence if available
        if match_request.resume.extracted_skills:
            for skill_detail in match_request.resume.extracted_skills:
                if skill_detail.evidence:
                    skill_snips = self.snippet_extractor.extract_snippets_from_text(skill_detail.evidence)
                    for snip in skill_snips:
                        low = snip.lower()
                        if low not in seen_lower:
                            seen_lower.add(low)
                            snippets.append(snip)

        return snippets

    def evaluate_semantic_evidence(
        self, match_request: MatchRequest
    ) -> Tuple[List[SemanticEvidenceMatch], float]:
        """
        Performs requirement-level semantic evidence matching between job requirements and candidate resume evidence.
        """
        job_reqs = match_request.job.requirements

        if not job_reqs:
            return [], 100.0

        candidate_snippets = self.extract_candidate_snippets(match_request)

        semantic_matches: List[SemanticEvidenceMatch] = []
        scores: List[float] = []

        for req in job_reqs:
            req_text = (req.evidence or req.skill or "").strip()
            if not req_text:
                semantic_matches.append(
                    SemanticEvidenceMatch(
                        requirement_skill=req.skill,
                        requirement_evidence=req.evidence or "",
                        best_matching_resume_evidence=None,
                        similarity_score=0.0,
                    )
                )
                scores.append(0.0)
                continue

            best_evidence: Optional[str] = None
            best_sim_score: float = 0.0

            if candidate_snippets:
                for snippet in candidate_snippets:
                    snippet_lower = snippet.lower()
                    sim_ev = self.similarity_svc.compute_similarity(req_text, snippet).similarity_score
                    sim_skill = (
                        self.similarity_svc.compute_similarity(req.skill, snippet).similarity_score
                        if req.skill
                        else 0.0
                    )
                    score = max(sim_ev, sim_skill)

                    # Boost score if candidate snippet explicitly contains the skill name
                    if req.skill and len(req.skill.strip()) > 1 and req.skill.lower() in snippet_lower:
                        score = max(score, 0.50)

                    # For REST API / API requirements, prefer specific implementation/project bullets over generic summary lines
                    is_api_req = any(
                        k in (req.skill or "").lower() or k in req_text.lower()
                        for k in ["rest api", "api", "fastapi", "backend service"]
                    )
                    if is_api_req:
                        api_keywords = {"rest api", "rest apis", "fastapi", "backend apis", "backend api", "api development", "api services", "microservices"}
                        matched_kw = sum(1 for kw in api_keywords if kw in snippet_lower)
                        if matched_kw > 0 and not snippet_lower.startswith(("software engineer with", "summary", "profile")):
                            score += 0.15 * matched_kw

                    # Ensure candidate snippet score is strictly bounded in normalized range [0.0, 1.0]
                    score = min(max(score, 0.0), 1.0)

                    if score > best_sim_score:
                        best_sim_score = score
                        best_evidence = snippet

            # Apply similarity threshold and guarantee final score is bounded in [0.0, 1.0]
            if best_sim_score >= self.similarity_threshold:
                final_evidence = best_evidence
                final_score = min(max(best_sim_score, 0.0), 1.0)
            else:
                final_evidence = None
                final_score = 0.0

            semantic_matches.append(
                SemanticEvidenceMatch(
                    requirement_skill=req.skill,
                    requirement_evidence=req.evidence or req_text,
                    best_matching_resume_evidence=final_evidence,
                    similarity_score=final_score,
                )
            )
            scores.append(final_score)

        avg_sim_score = (sum(scores) / len(scores)) if scores else 1.0
        sub_score = avg_sim_score * 100.0
        return semantic_matches, sub_score

    def generate_summary(
        self,
        overall_score: float,
        matched_req: List[str],
        missing_req: List[str],
        matched_pref: List[str],
        missing_pref: List[str],
        exp_assessment: ExperienceAssessment,
    ) -> str:
        """
        Generates plain-language match summary string.
        """
        parts = [f"Overall Match Score: {overall_score:.1f}/100."]

        if missing_req:
            parts.append(
                f"Matched {len(matched_req)}/{len(matched_req) + len(missing_req)} required skills ({', '.join(matched_req) or 'None'}). Missing: {', '.join(missing_req)}."
            )
        else:
            parts.append(f"Matched all required skills ({', '.join(matched_req) or 'None'}).")

        if matched_pref or missing_pref:
            parts.append(
                f"Matched {len(matched_pref)}/{len(matched_pref) + len(missing_pref)} preferred skills."
            )

        if exp_assessment.status == "matched":
            parts.append(f"Candidate meets minimum experience requirement ({exp_assessment.candidate_years}y vs {exp_assessment.required_years}y required).")
        elif exp_assessment.status == "below_requirement":
            parts.append(f"Candidate experience is below requirement ({exp_assessment.candidate_years}y vs {exp_assessment.required_years}y required).")
        else:
            parts.append("Experience requirement or candidate experience unavailable.")

        return " ".join(parts)

    def match(self, request: MatchRequest) -> MatchResponse:
        """
        Executes full explainable match analysis between candidate resume data and job requirements.
        """
        resume = request.resume
        job = request.job

        # 1. Exact Skill Matching
        matched_req, missing_req, matched_pref, missing_pref = self.evaluate_exact_skills(
            resume.skills, job.required_skills, job.preferred_skills
        )

        total_req = len(job.required_skills)
        score_req = (len(matched_req) / total_req * 100.0) if total_req > 0 else 100.0

        total_pref = len(job.preferred_skills)
        score_pref = (len(matched_pref) / total_pref * 100.0) if total_pref > 0 else 100.0

        # 2. Experience Fit Assessment
        exp_assessment, score_exp, exp_active = self.evaluate_experience(
            resume.candidate_experience_years, job.minimum_experience_years
        )

        # 3. Requirement-Level Semantic Evidence Matching
        semantic_matches, score_sem = self.evaluate_semantic_evidence(request)

        # 4. Weighted Score Calculation with Dynamic Weight Normalization
        w_req = self.w_required
        w_pref = self.w_preferred
        w_sem = self.w_semantic
        w_exp = self.w_experience if exp_active else 0.0

        total_weight = w_req + w_pref + w_sem + w_exp
        if total_weight <= 0:
            total_weight = 1.0

        weighted_sum = (
            (w_req * score_req)
            + (w_pref * score_pref)
            + (w_sem * score_sem)
            + (w_exp * score_exp)
        )

        raw_overall = weighted_sum / total_weight
        clamped_overall = max(0.0, min(100.0, raw_overall))
        overall_score = round(clamped_overall, 2)

        # 5. Summary Generation
        summary_text = self.generate_summary(
            overall_score, matched_req, missing_req, matched_pref, missing_pref, exp_assessment
        )

        return MatchResponse(
            overall_score=overall_score,
            matched_required_skills=matched_req,
            missing_required_skills=missing_req,
            matched_preferred_skills=matched_pref,
            missing_preferred_skills=missing_pref,
            experience_assessment=exp_assessment,
            semantic_evidence_matches=semantic_matches,
            summary=summary_text,
        )


# Global singleton instance
matching_engine = MatchingEngine()
