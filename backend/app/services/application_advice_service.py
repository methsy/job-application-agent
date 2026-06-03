from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.models.match_score import MatchScore
from app.schemas.application_advice import ApplicationAdviceRead


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

    risk_notes = build_risk_notes(
        match_score=match_score,
        job_requirement=job_requirement,
    )

    cover_letter_angle = build_cover_letter_angle(
        best_cv_angle=best_cv_angle,
        job_requirement=job_requirement,
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
