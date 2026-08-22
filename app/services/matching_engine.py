import re
from typing import List, Optional, Tuple, Set
from app.core.taxonomy import SKILL_TAXONOMY
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
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        candidate_snippets: Optional[List[str]] = None,
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """
        Calculates exact canonical skill matches and missing skill lists for required and preferred skills.
        Supports both taxonomy-recognized skills and non-taxonomy explicit job requirements.
        """
        cand_set_lower = {s.lower() for s in candidate_skills}

        def _is_matched(skill_name: str) -> bool:
            if not skill_name or not skill_name.strip():
                return False
            s_clean = skill_name.strip()
            s_low = s_clean.lower()
            if s_low in cand_set_lower:
                return True
            if candidate_snippets:
                skill_aliases = self._get_skill_aliases(s_clean)
                for snippet in candidate_snippets:
                    if self._has_skill_mention(snippet, s_clean, skill_aliases):
                        return True
            return False

        matched_req = [s for s in required_skills if _is_matched(s)]
        missing_req = [s for s in required_skills if not _is_matched(s)]

        matched_pref = [s for s in preferred_skills if _is_matched(s)]
        missing_pref = [s for s in preferred_skills if not _is_matched(s)]

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

    def _get_skill_aliases(self, skill_name: Optional[str]) -> Set[str]:
        """Returns a set of lowercase aliases for a given skill name using SKILL_TAXONOMY or default bounds."""
        if not skill_name or not skill_name.strip():
            return set()

        skill_clean = skill_name.strip()
        skill_low = skill_clean.lower()
        aliases = {skill_low}

        for category, skills in SKILL_TAXONOMY.items():
            for canonical_name, alias_list in skills.items():
                if canonical_name.lower() == skill_low:
                    aliases.add(canonical_name.lower())
                    aliases.update(a.lower() for a in alias_list)

        # Handle specific common tool acronyms / synonyms
        if skill_low == "aws":
            aliases.update(["aws", "amazon web services"])
        elif skill_low == "git":
            aliases.update(["git", "github"])
        elif skill_low == "github":
            aliases.update(["github", "git"])
        elif skill_low == "gitlab":
            aliases.update(["gitlab"])
        elif skill_low == "gcp":
            aliases.update(["gcp", "google cloud", "google cloud platform"])
        elif skill_low == "azure":
            aliases.update(["azure", "microsoft azure"])
        elif skill_low == "linux":
            aliases.update(["linux", "unix", "ubuntu", "debian", "centos", "rhel"])
        elif skill_low == "ci/cd":
            aliases.update(["ci/cd", "ci-cd", "continuous integration", "continuous deployment"])
        elif skill_low == "computer vision":
            aliases.update(["computer vision", "cv", "yolo", "yolov5", "opencv"])
        elif skill_low in ["photoshop", "adobe photoshop"]:
            aliases.update(["photoshop", "adobe photoshop"])
        elif skill_low in ["illustrator", "adobe illustrator"]:
            aliases.update(["illustrator", "adobe illustrator"])
        elif skill_low in ["after effects", "adobe after effects"]:
            aliases.update(["after effects", "adobe after effects"])
        elif skill_low in ["premiere pro", "adobe premiere pro", "premiere"]:
            aliases.update(["premiere pro", "adobe premiere pro", "premiere"])
        elif skill_low in ["ui/ux design", "ui/ux", "user interface design"]:
            aliases.update(["ui/ux design", "ui/ux", "user interface design"])

        return aliases

    def _is_explicit_technical_skill(self, req_skill: Optional[str], req_text: str) -> bool:
        """
        Determines whether a job requirement is for an explicit technology, tool, or skill
        (e.g., Docker, Terraform, Kubernetes, Linux, AWS, Python, Git, Photoshop, Figma, etc.)
        versus a broad conceptual requirement (e.g., "backend API development").
        """
        if not req_skill or not req_skill.strip():
            return False

        req_skill_low = req_skill.strip().lower()

        # Check if req_skill is in SKILL_TAXONOMY
        for category, skills in SKILL_TAXONOMY.items():
            for canonical_name, alias_list in skills.items():
                if canonical_name.lower() == req_skill_low or req_skill_low in [a.lower() for a in alias_list]:
                    return True

        # Common explicit technical, design, and software tools
        common_tools = {
            "docker", "terraform", "kubernetes", "k8s", "linux", "gitlab", "gcp",
            "azure", "ansible", "prometheus", "aws", "python", "git", "github",
            "react", "mongodb", "postgresql", "fastapi", "django", "flask",
            "photoshop", "adobe photoshop", "illustrator", "adobe illustrator",
            "figma", "after effects", "premiere pro", "autocad", "sap", "salesforce",
            "ui/ux design", "brand identity", "typography", "motion graphics"
        }
        if req_skill_low in common_tools or len(req_skill.strip().split()) <= 4:
            return True

        return False


    def _has_skill_mention(self, snippet: str, skill_name: Optional[str], skill_aliases: Set[str]) -> bool:
        """
        Checks if snippet explicitly mentions skill_name or any of its taxonomy aliases.
        Uses boundary-aware regex matching to avoid false positives (e.g. 'java' inside 'javascript').
        """
        if not snippet or not (skill_name or skill_aliases):
            return False

        snippet_lower = snippet.lower()
        all_targets = set(skill_aliases)
        if skill_name:
            all_targets.add(skill_name.strip().lower())

        for target in all_targets:
            if not target or len(target) < 2:
                continue
            escaped = re.escape(target)
            if target.endswith(("+", "#")):
                trailing = r"(?![\w\+#])"
            else:
                trailing = r"(?![\w\+#]|\.\w)"

            if target.startswith("."):
                leading = r"(?<![\w\+#\-])"
            else:
                leading = r"(?<![\w\+#\.-])"

            pattern = re.compile(leading + escaped + trailing, re.IGNORECASE)
            if pattern.search(snippet_lower):
                return True

        return False

    def evaluate_semantic_evidence(
        self, match_request: MatchRequest
    ) -> Tuple[List[SemanticEvidenceMatch], float]:
        """
        Performs requirement-level semantic evidence matching between job requirements and candidate resume evidence.
        Applies high-precision evidence acceptance rules to prevent weak false positives.
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

            is_explicit_tech = self._is_explicit_technical_skill(req.skill, req_text)
            skill_aliases = self._get_skill_aliases(req.skill) if req.skill else set()

            best_evidence: Optional[str] = None
            best_sim_score: float = 0.0

            if candidate_snippets:
                for snippet in candidate_snippets:
                    snippet_lower = snippet.lower()
                    has_mention = self._has_skill_mention(snippet, req.skill, skill_aliases)

                    # 1. Explicit Technical Skill Requirements (Docker, Terraform, Linux, Kubernetes, etc.):
                    # Direct skill or alias presence is required for evidence acceptance.
                    # Semantic similarity alone is NOT sufficient for an unrelated explicit technical skill.
                    if is_explicit_tech:
                        if not has_mention:
                            continue  # Reject snippet as evidence for missing explicit technical skill

                        sim_ev = self.similarity_svc.compute_similarity(req_text, snippet).similarity_score
                        sim_skill = (
                            self.similarity_svc.compute_similarity(req.skill, snippet).similarity_score
                            if req.skill
                            else 0.0
                        )
                        score = max(sim_ev, sim_skill, 0.50)

                        # Prefer specific project/implementation bullets for API/REST requirements
                        is_api_req = any(
                            k in (req.skill or "").lower() or k in req_text.lower()
                            for k in ["rest api", "api", "fastapi", "backend service"]
                        )
                        if is_api_req:
                            api_keywords = {"rest api", "rest apis", "fastapi", "backend apis", "backend api", "api development", "api services", "microservices"}
                            matched_kw = sum(1 for kw in api_keywords if kw in snippet_lower)
                            if matched_kw > 0 and not snippet_lower.startswith(("software engineer with", "summary", "profile")):
                                score += 0.15 * matched_kw

                    # 2. Conceptual Requirements (e.g. "backend API development"):
                    # Semantic similarity plays a primary role, requiring a strong threshold (>= 0.45).
                    else:
                        sim_ev = self.similarity_svc.compute_similarity(req_text, snippet).similarity_score
                        sim_skill = (
                            self.similarity_svc.compute_similarity(req.skill, snippet).similarity_score
                            if req.skill
                            else 0.0
                        )
                        raw_sim = max(sim_ev, sim_skill)
                        if has_mention:
                            score = max(raw_sim, 0.50)
                        elif raw_sim >= 0.45:
                            score = raw_sim
                        else:
                            continue  # Reject weak generic sentence for conceptual requirement

                    score = min(max(score, 0.0), 1.0)

                    if score > best_sim_score:
                        best_sim_score = score
                        best_evidence = snippet

            # Apply similarity threshold and guarantee final score is bounded in [0.0, 1.0]
            if best_sim_score >= self.similarity_threshold and best_sim_score > 0.0:
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

        if not job or (
            not (job.required_skills and len(job.required_skills) > 0)
            and not (job.preferred_skills and len(job.preferred_skills) > 0)
            and job.minimum_experience_years is None
            and not (job.requirements and len(job.requirements) > 0)
        ):
            raise ValueError(
                "Insufficient job description. Please provide meaningful requirements, "
                "skills, responsibilities, or experience criteria to calculate a match score."
            )

        candidate_snippets = self.extract_candidate_snippets(request)

        # 1. Exact Skill Matching (evaluates taxonomy and non-taxonomy skills)
        matched_req, missing_req, matched_pref, missing_pref = self.evaluate_exact_skills(
            resume.skills, job.required_skills, job.preferred_skills, candidate_snippets
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
