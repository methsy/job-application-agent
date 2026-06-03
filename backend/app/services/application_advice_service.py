from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.models.match_score import MatchScore
from app.schemas.application_advice import ApplicationAdviceRead

KEYWORD_DISPLAY_OVERRIDES = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "fastapi": "FastAPI",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "aws": "AWS",
    "api": "API",
    "apis": "APIs",
    "rest api": "REST API",
    "rest apis": "REST APIs",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "ml": "ML",
    "ai": "AI",
    "ml/ai": "ML/AI",
    "ml/ai frameworks": "ML/AI frameworks",
    "ml/ai solutions": "ML/AI solutions",
    "scalable system design": "Scalable system design",
    "software engineering": "Software engineering",
    "software engineer": "Software Engineer",
    "python developer": "Python developer",
    "automation": "Automation",
    "testing": "Testing",
    "cloud": "Cloud",
    "cloud systems": "Cloud systems",
    "data engineering": "Data engineering",
    "data integration": "Data integration",
}


def generate_application_advice(
    match_score: MatchScore,
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
) -> ApplicationAdviceRead:
    decision = get_application_decision(match_score)

    best_cv_angle = build_best_cv_angle(
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    keywords_to_add = build_keywords_to_add(
        match_score=match_score,
        job_requirement=job_requirement,
    )

    keywords_to_add = _clean_keyword_list(keywords_to_add)

    risk_notes = _build_risk_notes(
        missing_required_skills=match_score.missing_required_skills or [],
        gaps=match_score.gaps or [],
        keywords_to_add=keywords_to_add,
        recommendation=match_score.recommendation or decision,
    )

    cover_letter_angle = _build_cover_letter_angle(
        best_cv_angle=best_cv_angle,
        matched_skills=match_score.matched_skills or [],
        matched_responsibilities=match_score.matched_responsibilities or [],
        keywords_to_add=keywords_to_add,
    )

    next_action = build_next_action(
        decision=decision,
        match_score=match_score,
    )

    return ApplicationAdviceRead(
        decision=decision,
        best_cv_angle=best_cv_angle,
        keywords_to_add=keywords_to_add,
        risk_notes=risk_notes,
        cover_letter_angle=cover_letter_angle,
        next_action=next_action,
    )


def get_application_decision(match_score: MatchScore) -> str:
    recommendation = match_score.recommendation

    if recommendation == "Apply":
        return "Apply"

    if recommendation in {"Review", "Maybe"}:
        return "Review"

    return "Skip"


def build_best_cv_angle(
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
) -> str:
    domain = (job_requirement.domain or "").lower()

    if "ai" in domain or "machine learning" in domain or "ml" in domain:
        return "Python software engineering with AI/ML and developer tooling angle"

    if "backend" in domain or "software engineering" in domain:
        return "Backend/API focused software engineering CV"

    if "data" in domain:
        return "Data-intensive systems and integration focused CV"

    if candidate_profile.target_roles:
        return f"{candidate_profile.target_roles[0]} focused CV"

    return "General software engineering CV"


def build_keywords_to_add(
    match_score: MatchScore,
    job_requirement: JobRequirement,
) -> list[str]:
    keywords: list[str] = []

    keywords.extend(job_requirement.required_skills or [])
    keywords.extend(job_requirement.preferred_skills or [])
    keywords.extend(job_requirement.keywords_for_ats or [])
    keywords.extend(match_score.matched_skills or [])
    keywords.extend(match_score.matched_preferred_skills or [])

    return deduplicate_preserving_order(keywords)


def build_risk_notes(
    match_score: MatchScore,
    job_requirement: JobRequirement,
) -> list[str]:
    risk_notes: list[str] = []

    for skill in match_score.missing_required_skills or []:
        risk_notes.append(
            f"Required skill needs evidence or review: {skill}"
        )

    for gap in match_score.gaps or []:
        risk_notes.append(gap)

    if match_score.technical_skill_score < 20:
        risk_notes.append(
            "Technical skill match is relatively low; review whether the CV clearly shows the required technologies."
        )

    if match_score.responsibility_score < 10:
        risk_notes.append(
            "Responsibility match is relatively low; review whether the CV clearly describes similar delivery responsibilities."
        )

    if match_score.domain_score < 6:
        risk_notes.append(
            "Domain match is weak or unclear; emphasise transferable domain experience."
        )

    if job_requirement.nice_to_have:
        risk_notes.append(
            "Review nice-to-have requirements and mention any relevant evidence where truthful."
        )

    return deduplicate_preserving_order(risk_notes)


def build_cover_letter_angle(
    best_cv_angle: str,
    job_requirement: JobRequirement,
) -> str:
    domain = job_requirement.domain or "the role"

    return (
        f"Position the application around {best_cv_angle.lower()}, "
        f"with emphasis on evidence that matches {domain}, the required skills, "
        "and the most relevant delivery responsibilities."
    )


def build_next_action(
    decision: str,
    match_score: MatchScore,
) -> str:
    if decision == "Apply":
        return (
            "Proceed to tailor the CV and prepare a focused cover letter using the matched skills, "
            "responsibilities, and ATS keywords."
        )

    if decision == "Review":
        if match_score.gaps:
            return (
                "Review the listed gaps, then decide whether to tailor the CV or skip the role."
            )

        return (
            "Review the role manually, then tailor the CV if the opportunity is strategically worthwhile."
        )

    return (
        "Skip or save only if there is a strategic reason to revisit later."
    )


def deduplicate_preserving_order(values: list[str]) -> list[str]:
    seen = set()
    result = []

    for value in values:
        cleaned = str(value).strip()

        if not cleaned:
            continue

        normalized = cleaned.lower()

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(cleaned)

    return result


def get_application_advice_by_match_score_id(
    db: Session,
    match_score_id: str,
) -> ApplicationAdviceRead | None:
    match_score = (
        db.query(MatchScore)
        .filter(MatchScore.id == match_score_id)
        .first()
    )

    if not match_score:
        return None

    candidate_profile = (
        db.query(CandidateProfile)
        .filter(CandidateProfile.id == match_score.candidate_profile_id)
        .first()
    )

    job_requirement = (
        db.query(JobRequirement)
        .filter(JobRequirement.id == match_score.job_requirement_id)
        .first()
    )

    if not candidate_profile or not job_requirement:
        return None

    return generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )


def _format_keyword_display(keyword: str) -> str:
    """
    Convert internal keyword strings into clean user-facing display text.

    Examples:
    - "python" -> "Python"
    - "ci/cd" -> "CI/CD"
    - "ml/aI frameworks" -> "ML/AI frameworks"
    """
    if not keyword:
        return keyword

    normalized = " ".join(keyword.strip().split())
    lookup_key = normalized.lower()

    if lookup_key in KEYWORD_DISPLAY_OVERRIDES:
        return KEYWORD_DISPLAY_OVERRIDES[lookup_key]

    # Handle common mixed-case AI/ML variants inside longer phrases.
    formatted = normalized
    formatted = formatted.replace("ml/aI", "ML/AI")
    formatted = formatted.replace("ML/aI", "ML/AI")
    formatted = formatted.replace("ml/ai", "ML/AI")
    formatted = formatted.replace("ai/ml", "AI/ML")
    formatted = formatted.replace("ci/cd", "CI/CD")
    formatted = formatted.replace("api", "API")

    # If no specific rule matched, make the first character uppercase.
    return formatted[:1].upper() + formatted[1:]


def _clean_keyword_list(keywords: list[str]) -> list[str]:
    """
    Format and deduplicate keyword suggestions while preserving order.
    """
    cleaned: list[str] = []
    seen: set[str] = set()

    for keyword in keywords:
        display_keyword = _format_keyword_display(keyword)
        dedupe_key = display_keyword.lower()

        if display_keyword and dedupe_key not in seen:
            cleaned.append(display_keyword)
            seen.add(dedupe_key)

    return cleaned


def _build_cover_letter_angle(
    best_cv_angle: str,
    matched_skills: list[str],
    matched_responsibilities: list[str],
    keywords_to_add: list[str],
) -> str:
    """
    Build a more natural cover letter positioning statement.
    Keep this deterministic and based only on available scoring/advice evidence.
    """

    evidence_terms = _clean_keyword_list(
        matched_skills + matched_responsibilities + keywords_to_add
    )

    priority_terms = _select_cover_letter_focus_terms(evidence_terms)

    if priority_terms:
        focus_text = ", ".join(priority_terms[:-1])

        if len(priority_terms) > 1:
            focus_text = f"{focus_text}, and {priority_terms[-1]}"
        else:
            focus_text = priority_terms[0]

        return (
            f"Position the application around {best_cv_angle.replace(' CV', '').lower()}, "
            f"with emphasis on {focus_text}."
        )

    return (
        f"Position the application around {best_cv_angle.replace(' CV', '').lower()}, "
        "with emphasis on the strongest matching technical skills, delivery experience, "
        "and role-relevant achievements."
    )


def _select_cover_letter_focus_terms(evidence_terms: list[str]) -> list[str]:
    """
    Select a small number of strong, user-facing focus terms for cover letter guidance.
    """

    focus_rules = [
        ("Python", ["python"]),
        ("backend/API software engineering", ["backend", "api", "apis", "software engineering"]),
        ("cloud/API integration", ["cloud", "api integration", "apis", "api"]),
        ("data-intensive systems", ["data engineering", "data integration", "data"]),
        ("testing", ["testing", "quality"]),
        ("CI/CD", ["ci/cd", "cicd"]),
        ("automation", ["automation"]),
        ("prototype-to-production delivery", ["production", "delivery"]),
        ("scalable system design", ["scalable system design", "architecture", "design"]),
        ("ML/AI frameworks", ["ml/ai", "ai", "ml"]),
    ]

    normalized_terms = [term.lower() for term in evidence_terms]

    selected: list[str] = []

    for display_text, triggers in focus_rules:
        if any(
            trigger in term
            for trigger in triggers
            for term in normalized_terms
        ):
            if display_text not in selected:
                selected.append(display_text)

    return selected[:6]


def _build_risk_notes(
    missing_required_skills: list[str],
    gaps: list[str],
    keywords_to_add: list[str],
    recommendation: str,
) -> list[str]:
    """
    Build specific, practical risk notes instead of generic advice.
    """

    notes: list[str] = []

    normalized_gaps = [gap.lower() for gap in gaps or []]
    normalized_keywords = [keyword.lower() for keyword in keywords_to_add or []]
    normalized_missing = [skill.lower() for skill in missing_required_skills or []]

    if any("ml" in item or "ai" in item for item in normalized_keywords + normalized_gaps + normalized_missing):
        notes.append("Clarify depth of hands-on ML/AI framework experience.")

    if any("ci/cd" in item or "testing" in item or "automation" in item for item in normalized_keywords + normalized_gaps):
        notes.append("Emphasise CI/CD, testing, automation, and quality engineering examples.")

    if any("production" in item or "prototype" in item for item in normalized_keywords + normalized_gaps):
        notes.append("Show evidence of moving software from prototype to production.")

    if any("cloud" in item for item in normalized_keywords + normalized_gaps + normalized_missing):
        notes.append("Clarify practical cloud experience and any AWS-relevant project evidence.")

    if any("scalable" in item or "architecture" in item or "design" in item for item in normalized_keywords + normalized_gaps):
        notes.append("Use concrete examples of scalable system design or architecture decisions.")

    if missing_required_skills:
        missing_display = ", ".join(_clean_keyword_list(missing_required_skills))
        notes.append(f"Review whether the CV can truthfully address these missing or weak areas: {missing_display}.")

    if recommendation.lower() == "review":
        notes.append("Before applying, confirm that all hard requirements are genuinely satisfied.")

    notes.append("Mention nice-to-have requirements only where truthful.")

    return _dedupe_notes(notes)


def _dedupe_notes(notes: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()

    for note in notes:
        key = note.lower().strip()
        if key and key not in seen:
            cleaned.append(note)
            seen.add(key)

    return cleaned
