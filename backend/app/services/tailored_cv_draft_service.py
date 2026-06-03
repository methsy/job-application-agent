from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.models.match_score import MatchScore
from app.schemas.application_advice import ApplicationAdviceRead
from app.schemas.tailored_cv_draft import TailoredCvDraftResponse


def generate_tailored_cv_draft(
    match_score: MatchScore,
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
    application_advice: ApplicationAdviceRead,
) -> TailoredCvDraftResponse:
    skills_to_emphasise = _build_skills_to_emphasise(
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
        match_score=match_score,
        application_advice=application_advice,
    )

    experience_themes = _build_experience_themes(
        match_score=match_score,
        job_requirement=job_requirement,
    )

    target_headline = _build_target_headline(application_advice.best_cv_angle)

    professional_summary = _build_professional_summary(
        target_headline=target_headline,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
        skills_to_emphasise=skills_to_emphasise,
        experience_themes=experience_themes,
    )

    ats_keywords = _dedupe_preserve_order(
        application_advice.keywords_to_add
        + (job_requirement.keywords_for_ats or [])
        + (match_score.matched_skills or [])
        + (match_score.matched_preferred_skills or [])
    )

    draft_text = _build_draft_text(
        target_headline=target_headline,
        professional_summary=professional_summary,
        skills_to_emphasise=skills_to_emphasise,
        experience_themes=experience_themes,
        ats_keywords=ats_keywords,
        risk_notes=application_advice.risk_notes,
    )

    return TailoredCvDraftResponse(
        cv_angle=application_advice.best_cv_angle,
        target_headline=target_headline,
        professional_summary=professional_summary,
        skills_to_emphasise=skills_to_emphasise,
        experience_themes=experience_themes,
        ats_keywords=ats_keywords,
        risk_notes=application_advice.risk_notes,
        draft_text=draft_text,
    )


def _build_target_headline(cv_angle: str) -> str:
    normalized = cv_angle.replace(" CV", "").strip()

    if "backend" in normalized.lower() and "api" in normalized.lower():
        return "Backend/API Software Engineer"

    if "data" in normalized.lower() and "integration" in normalized.lower():
        return "Data and Integration Developer"

    if "full stack" in normalized.lower() or "fullstack" in normalized.lower():
        return "Full Stack Software Engineer"

    if normalized:
        return normalized

    return "Software Engineer"


def _build_skills_to_emphasise(
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
    match_score: MatchScore,
    application_advice: ApplicationAdviceRead,
) -> list[str]:
    skills = []

    skills.extend(match_score.matched_skills or [])
    skills.extend(match_score.matched_preferred_skills or [])
    skills.extend(application_advice.keywords_to_add or [])

    candidate_skills = (
        (candidate_profile.core_skills or [])
        + (candidate_profile.secondary_skills or [])
    )

    required_and_preferred = (
        (job_requirement.required_skills or [])
        + (job_requirement.preferred_skills or [])
    )

    for candidate_skill in candidate_skills:
        if _matches_any(candidate_skill, required_and_preferred):
            skills.append(candidate_skill)

    return _dedupe_preserve_order([_clean_display_text(skill) for skill in skills])[:12]


def _build_experience_themes(
    match_score: MatchScore,
    job_requirement: JobRequirement,
) -> list[str]:
    themes = []

    combined_text = " ".join(
        (match_score.matched_responsibilities or [])
        + (job_requirement.responsibilities or [])
    ).lower()

    if "api" in combined_text:
        themes.append("Backend API design, implementation, and integration")

    if "test" in combined_text or "quality" in combined_text:
        themes.append("Testing, validation, and quality-focused delivery")

    if "automation" in combined_text:
        themes.append("Automation and process improvement")

    if "production" in combined_text or "delivery" in combined_text:
        themes.append("Prototype-to-production software delivery")

    if "cloud" in combined_text:
        themes.append("Cloud-aware application development and deployment")

    if "data" in combined_text:
        themes.append("Data-intensive systems and integration workflows")

    if "architecture" in combined_text or "design" in combined_text or "scalable" in combined_text:
        themes.append("Scalable system design and maintainable architecture")

    if not themes:
        themes.append("Relevant software engineering delivery experience")

    return _dedupe_preserve_order(themes)


def _build_professional_summary(
    target_headline: str,
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
    skills_to_emphasise: list[str],
    experience_themes: list[str],
) -> str:
    top_skills = ", ".join(skills_to_emphasise[:5])
    top_themes = ", ".join(experience_themes[:2])

    seniority = candidate_profile.seniority or "Experienced"

    domain = job_requirement.domain or _first_or_default(
        candidate_profile.domains,
        "software engineering",
    )

    return (
        f"{seniority} {target_headline} with a background in {domain}. "
        f"Strong alignment with this role through {top_skills}. "
        f"The CV should emphasise {top_themes}, with concrete examples and measurable outcomes where truthful."
    )


def _build_draft_text(
    target_headline: str,
    professional_summary: str,
    skills_to_emphasise: list[str],
    experience_themes: list[str],
    ats_keywords: list[str],
    risk_notes: list[str],
) -> str:
    skills_text = "\n".join(f"- {skill}" for skill in skills_to_emphasise)
    themes_text = "\n".join(f"- {theme}" for theme in experience_themes)
    keywords_text = ", ".join(ats_keywords)
    risks_text = "\n".join(f"- {note}" for note in risk_notes)

    return (
        f"{target_headline}\n\n"
        f"Professional Summary\n"
        f"{professional_summary}\n\n"
        f"Skills to Emphasise\n"
        f"{skills_text}\n\n"
        f"Experience Themes to Bring Forward\n"
        f"{themes_text}\n\n"
        f"ATS Keywords to Include Where Truthful\n"
        f"{keywords_text}\n\n"
        f"Review Before Using\n"
        f"{risks_text}"
    )


def _matches_any(value: str, candidates: list[str]) -> bool:
    value_lower = value.lower()

    return any(
        value_lower in candidate.lower() or candidate.lower() in value_lower
        for candidate in candidates
    )


def _clean_display_text(value: str) -> str:
    cleaned = " ".join(value.strip().split())

    overrides = {
        "python": "Python",
        "ci/cd": "CI/CD",
        "ml/ai": "ML/AI",
        "ml/ai frameworks": "ML/AI frameworks",
        "api": "API",
        "apis": "APIs",
        "aws": "AWS",
        "sql": "SQL",
        "postgresql": "PostgreSQL",
        "fastapi": "FastAPI",
    }

    lower = cleaned.lower()

    if lower in overrides:
        return overrides[lower]

    cleaned = cleaned.replace("ml/aI", "ML/AI")
    cleaned = cleaned.replace("ml/ai", "ML/AI")
    cleaned = cleaned.replace("ci/cd", "CI/CD")

    return cleaned[:1].upper() + cleaned[1:]


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    result = []
    seen = set()

    for value in values:
        if not value:
            continue

        cleaned = _clean_display_text(value)
        key = cleaned.lower()

        if key not in seen:
            result.append(cleaned)
            seen.add(key)

    return result


def _first_or_default(values: list[str], default: str) -> str:
    if values:
        return values[0]

    return default
