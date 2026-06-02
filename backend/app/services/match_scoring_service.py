from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.schemas.match_score import MatchScoreCalculated


def calculate_match_score(
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
) -> MatchScoreCalculated:
    candidate_skills = normalize_list(
        candidate_profile.core_skills + candidate_profile.secondary_skills
    )
    required_skills = normalize_list(job_requirement.required_skills)
    preferred_skills = normalize_list(job_requirement.preferred_skills)

    matched_required_skills = get_matches(
        candidate_profile.core_skills + candidate_profile.secondary_skills,
        job_requirement.required_skills,
    )

    matched_preferred_skills = get_matches(
        candidate_profile.core_skills + candidate_profile.secondary_skills,
        job_requirement.preferred_skills,
    )

    missing_required_skills = get_missing(
        candidate_skills=candidate_skills,
        required_skills=job_requirement.required_skills,
    )

    technical_skill_score = calculate_technical_skill_score(
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        matched_required_count=len(matched_required_skills),
        matched_preferred_count=len(matched_preferred_skills),
    )

    matched_responsibilities = match_responsibilities(
        candidate_domains=candidate_profile.domains,
        candidate_skills=candidate_profile.core_skills + candidate_profile.secondary_skills,
        candidate_target_roles=candidate_profile.target_roles,
        candidate_experience_summaries=candidate_profile.experience_summary,
        job_responsibilities=job_requirement.responsibilities,
    )

    responsibility_score = calculate_responsibility_score(
        job_responsibilities=job_requirement.responsibilities,
        matched_responsibilities=matched_responsibilities,
    )

    seniority_score = calculate_seniority_score(
        candidate_seniority=candidate_profile.seniority,
        job_seniority=job_requirement.seniority,
    )

    domain_score = calculate_domain_score(
        candidate_domains=candidate_profile.domains,
        job_domain=job_requirement.domain,
    )

    location_score = calculate_location_score(
        candidate_locations=candidate_profile.location_preferences,
        job_location=job_requirement.location,
        work_arrangement=job_requirement.work_arrangement,
    )

    constraints_score = calculate_constraints_score(
        hard_requirements=job_requirement.hard_requirements,
    )

    career_strategy_score = calculate_career_strategy_score(
        total_required_skills=len(required_skills),
        missing_required_skills=missing_required_skills,
    )

    total_score = (
        technical_skill_score
        + responsibility_score
        + seniority_score
        + domain_score
        + location_score
        + constraints_score
        + career_strategy_score
    )

    recommendation = get_recommendation(
        total_score=total_score,
        missing_required_skills=missing_required_skills,
        hard_requirements=job_requirement.hard_requirements,
    )

    gaps = build_gaps(
        missing_required_skills=missing_required_skills,
        hard_requirements=job_requirement.hard_requirements,
        job_seniority=job_requirement.seniority,
        candidate_seniority=candidate_profile.seniority,
    )

    reasoning_summary = build_reasoning_summary(
        total_score=total_score,
        recommendation=recommendation,
        matched_required_skills=matched_required_skills,
        matched_preferred_skills=matched_preferred_skills,
        missing_required_skills=missing_required_skills,
    )

    return MatchScoreCalculated(
        total_score=total_score,
        technical_skill_score=technical_skill_score,
        responsibility_score=responsibility_score,
        seniority_score=seniority_score,
        domain_score=domain_score,
        location_score=location_score,
        constraints_score=constraints_score,
        career_strategy_score=career_strategy_score,
        recommendation=recommendation,
        matched_skills=matched_required_skills,
        missing_required_skills=missing_required_skills,
        matched_preferred_skills=matched_preferred_skills,
        matched_responsibilities=matched_responsibilities,
        gaps=gaps,
        reasoning_summary=reasoning_summary,
    )


def normalize_text(value: str) -> str:
    return value.strip().lower().replace("-", " ")


def normalize_list(values: list[str]) -> list[str]:
    return [normalize_text(value) for value in values if value.strip()]


def get_matches(candidate_values: list[str], required_values: list[str]) -> list[str]:
    normalized_candidate_values = normalize_list(candidate_values)

    matches: list[str] = []

    for required_value in required_values:
        required_options = split_grouped_skill_requirement(required_value)

        if not required_options:
            required_options = [required_value]

        for option in required_options:
            normalized_option = normalize_text(option)

            if any(
                normalized_option == candidate_value
                or normalized_option in candidate_value
                or candidate_value in normalized_option
                for candidate_value in normalized_candidate_values
            ):
                matches.append(required_value)
                break

    return deduplicate_preserving_order(matches)


def get_missing(
    candidate_skills: list[str],
    required_skills: list[str],
) -> list[str]:
    missing: list[str] = []

    for required_skill in required_skills:
        required_options = split_grouped_skill_requirement(required_skill)

        if not required_options:
            required_options = [required_skill]

        matched = False

        for option in required_options:
            normalized_option = normalize_text(option)

            if any(
                normalized_option == candidate_skill
                or normalized_option in candidate_skill
                or candidate_skill in normalized_option
                for candidate_skill in candidate_skills
            ):
                matched = True
                break

        if not matched:
            missing.append(required_skill)

    return missing


def calculate_technical_skill_score(
    required_skills: list[str],
    preferred_skills: list[str],
    matched_required_count: int,
    matched_preferred_count: int,
) -> int:
    max_score = 35

    if not required_skills and not preferred_skills:
        return 20

    required_score = 0
    preferred_score = 0

    if required_skills:
        required_score = int((matched_required_count / len(required_skills)) * 28)

    if preferred_skills:
        preferred_score = int((matched_preferred_count / len(preferred_skills)) * 7)

    return min(max_score, required_score + preferred_score)


def calculate_responsibility_score(
    job_responsibilities: list[str],
    matched_responsibilities: list[str],
) -> int:
    max_score = 20

    if not job_responsibilities:
        return 10

    return int((len(matched_responsibilities) / len(job_responsibilities)) * max_score)


def calculate_seniority_score(
    candidate_seniority: str,
    job_seniority: str,
) -> int:
    max_score = 15

    candidate = normalize_text(candidate_seniority)
    job = normalize_text(job_seniority)

    if not job:
        return 10

    if not candidate:
        return 8

    if job in candidate or candidate in job:
        return max_score

    if job == "senior" and candidate in {"lead", "principal"}:
        return max_score

    if job in {"lead", "principal"} and candidate == "senior":
        return 10

    return 6


def calculate_domain_score(
    candidate_domains: list[str],
    job_domain: str,
) -> int:
    max_score = 10

    if not job_domain:
        return 6

    normalized_job_domain = normalize_text(job_domain)

    for domain in candidate_domains:
        normalized_candidate_domain = normalize_text(domain)

        if (
            normalized_job_domain == normalized_candidate_domain
            or normalized_job_domain in normalized_candidate_domain
            or normalized_candidate_domain in normalized_job_domain
        ):
            return max_score

    return 4


def calculate_location_score(
    candidate_locations: list[str],
    job_location: str,
    work_arrangement: str,
) -> int:
    max_score = 10

    normalized_work_arrangement = normalize_text(work_arrangement)
    normalized_job_location = normalize_text(job_location)
    normalized_candidate_locations = normalize_list(candidate_locations)

    if "remote" in normalized_work_arrangement:
        return max_score

    if not normalized_candidate_locations:
        return 7

    if any(
        location in normalized_job_location or normalized_job_location in location
        for location in normalized_candidate_locations
    ):
        return max_score

    if "hybrid" in normalized_work_arrangement:
        return 7

    return 4


def calculate_constraints_score(
    hard_requirements: list[str],
) -> int:
    max_score = 5

    if not hard_requirements:
        return max_score

    return 2


def calculate_career_strategy_score(
    total_required_skills: int,
    missing_required_skills: list[str],
) -> int:
    max_score = 5

    if total_required_skills == 0:
        return 3

    missing_count = len(missing_required_skills)

    if missing_count == 0:
        return max_score

    if missing_count <= 2:
        return 3

    return 1


def match_responsibilities(
    candidate_domains: list[str],
    job_responsibilities: list[str],
    candidate_skills: list[str] | None = None,
    candidate_target_roles: list[str] | None = None,
    candidate_experience_summaries: list[dict] | None = None,
) -> list[str]:
    candidate_skills = candidate_skills or []
    candidate_target_roles = candidate_target_roles or []
    candidate_experience_summaries = candidate_experience_summaries or []

    candidate_terms = []
    candidate_terms.extend(candidate_domains)
    candidate_terms.extend(candidate_skills)
    candidate_terms.extend(candidate_target_roles)

    for experience in candidate_experience_summaries:
        if isinstance(experience, dict):
            candidate_terms.append(str(experience.get("role", "")))
            candidate_terms.append(str(experience.get("summary", "")))

    normalized_candidate_terms = normalize_list(candidate_terms)

    responsibility_keywords = {
        "api": ["api", "rest"],
        "integration": ["integration", "integrate", "third-party", "enterprise systems"],
        "testing": ["testing", "unit", "integration test", "end-to-end"],
        "production support": ["production", "troubleshooting", "root-cause", "support"],
        "ci/cd": ["ci/cd", "pipeline", "deployment", "automation"],
        "monitoring": ["monitoring", "observability", "release management"],
        "architecture": ["architecture", "system design", "technical solutions"],
        "leadership": ["lead", "mentor", "coaching", "technical leadership"],
        "legacy systems": ["legacy", "refactoring", "re-engineering"],
        "scalability": ["scalable", "scalability", "resilience", "maintainability"],
    }

    matches: list[str] = []

    for responsibility in job_responsibilities:
        normalized_responsibility = normalize_text(responsibility)

        direct_match = any(
            term in normalized_responsibility
            or normalized_responsibility in term
            for term in normalized_candidate_terms
        )

        keyword_match = False

        for concept, keywords in responsibility_keywords.items():
            responsibility_has_concept = any(
                keyword in normalized_responsibility
                for keyword in keywords
            )

            candidate_has_concept = any(
                concept in term
                or any(keyword in term for keyword in keywords)
                for term in normalized_candidate_terms
            )

            if responsibility_has_concept and candidate_has_concept:
                keyword_match = True
                break

        if direct_match or keyword_match:
            matches.append(responsibility)

    return deduplicate_preserving_order(matches)


def get_recommendation(
    total_score: int,
    missing_required_skills: list[str],
    hard_requirements: list[str],
) -> str:
    if hard_requirements:
        return "Review"

    if total_score >= 75 and len(missing_required_skills) <= 2:
        return "Apply"

    if total_score >= 55:
        return "Maybe"

    return "Skip"


def build_gaps(
    missing_required_skills: list[str],
    hard_requirements: list[str],
    job_seniority: str,
    candidate_seniority: str,
) -> list[str]:
    gaps: list[str] = []

    for skill in missing_required_skills:
        gaps.append(f"Missing required skill: {skill}")

    for requirement in hard_requirements:
        gaps.append(f"Hard requirement needs review: {requirement}")

    if job_seniority and candidate_seniority:
        if normalize_text(job_seniority) not in normalize_text(candidate_seniority):
            gaps.append(
                f"Seniority mismatch needs review: job={job_seniority}, candidate={candidate_seniority}"
            )

    return gaps


def build_reasoning_summary(
    total_score: int,
    recommendation: str,
    matched_required_skills: list[str],
    matched_preferred_skills: list[str],
    missing_required_skills: list[str],
) -> str:
    return (
        f"Score {total_score}/100. Recommendation: {recommendation}. "
        f"Matched required skills: {', '.join(matched_required_skills) or 'none'}. "
        f"Matched preferred skills: {', '.join(matched_preferred_skills) or 'none'}. "
        f"Missing required skills: {', '.join(missing_required_skills) or 'none'}."
    )


def split_grouped_skill_requirement(requirement: str) -> list[str]:
    normalized = requirement.replace("/", " / ")

    separators = [",", " or ", " and "]

    for separator in separators:
        normalized = normalized.replace(separator, "|")

    parts = [
        part.strip()
        for part in normalized.split("|")
        if part.strip()
    ]

    cleaned_parts = []

    remove_phrases = [
        "at least one of",
        "one of",
        "exceptional proficiency in",
        "core language ie",
        "core language",
        "ie",
        "e.g.",
        "such as",
    ]

    for part in parts:
        cleaned = part.strip()

        for phrase in remove_phrases:
            cleaned = cleaned.replace(phrase, "")
            cleaned = cleaned.replace(phrase.title(), "")

        cleaned = cleaned.strip(" :;-")

        if cleaned:
            cleaned_parts.append(cleaned)

    return cleaned_parts


def deduplicate_preserving_order(values: list[str]) -> list[str]:
    seen = set()
    result = []

    for value in values:
        cleaned = value.strip()
        normalized = cleaned.lower()

        if not cleaned or normalized in seen:
            continue

        seen.add(normalized)
        result.append(cleaned)

    return result
