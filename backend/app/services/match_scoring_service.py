from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.schemas.match_score import MatchScoreCalculated

RESPONSIBILITY_CONCEPTS: dict[str, dict[str, list[str]]] = {
    "api_integration": {
        "job_keywords": [
            "api",
            "apis",
            "rest",
            "integration",
            "integrating",
            "third party",
            "third-party",
            "external service",
            "external services",
            "platform integration",
            "system integration",
            "systems integration",
        ],
        "candidate_keywords": [
            "api",
            "apis",
            "rest",
            "fastapi",
            "flask",
            "backend",
            "full stack",
            "integration",
            "integrations",
            "service",
            "services",
        ],
    },
    "cloud_systems": {
        "job_keywords": [
            "cloud",
            "cloud based",
            "cloud-based",
            "aws",
            "gcp",
            "azure",
            "cloud platform",
            "cloud platforms",
        ],
        "candidate_keywords": [
            "cloud",
            "aws",
            "gcp",
            "azure",
            "cloud based",
            "cloud-based",
            "deployment",
            "deployments",
        ],
    },
    "data_engineering": {
        "job_keywords": [
            "data",
            "data integration",
            "data integrations",
            "data pipeline",
            "data pipelines",
            "data platform",
            "data platforms",
            "database",
            "databases",
            "working with data",
        ],
        "candidate_keywords": [
            "data",
            "data pipeline",
            "data pipelines",
            "data intensive",
            "data-intensive",
            "sql",
            "postgresql",
            "database",
            "databases",
            "hpc",
            "etl",
        ],
    },
    "ai_ml_solutions": {
        "job_keywords": [
            "ai",
            "ml",
            "artificial intelligence",
            "machine learning",
            "ai backed",
            "ai-backed",
            "llm",
            "model",
            "models",
            "intelligent",
        ],
        "candidate_keywords": [
            "ai",
            "ml",
            "machine learning",
            "llm",
            "prompt engineering",
            "developer tooling",
            "ollama",
            "model",
            "models",
            "artificial intelligence",
        ],
    },
    "production_delivery": {
        "job_keywords": [
            "production",
            "prototype to production",
            "deliver",
            "delivering",
            "delivery",
            "deploy",
            "deployment",
            "shipping",
            "release",
        ],
        "candidate_keywords": [
            "production",
            "supported",
            "support",
            "maintained",
            "release",
            "deployment",
            "deploy",
            "ci cd",
            "ci/cd",
            "jenkins",
            "testing",
        ],
    },
    "testing_quality": {
        "job_keywords": [
            "test",
            "testing",
            "quality",
            "validation",
            "verification",
            "reliable",
            "reliability",
            "correctness",
        ],
        "candidate_keywords": [
            "test",
            "testing",
            "test driven development",
            "tdd",
            "pytest",
            "junit",
            "mockito",
            "jest",
            "validation",
            "verification",
            "reliability",
        ],
    },
    "architecture_design": {
        "job_keywords": [
            "architecture",
            "architectural",
            "system design",
            "technical design",
            "design",
            "designing",
            "solution design",
            "scalable",
            "scalability",
        ],
        "candidate_keywords": [
            "architecture",
            "system design",
            "technical design",
            "designed",
            "developed",
            "scalable",
            "maintainable",
            "backend",
            "full stack",
            "data intensive",
            "data-intensive",
        ],
    },
    "support_troubleshooting": {
        "job_keywords": [
            "support",
            "troubleshooting",
            "debugging",
            "defect",
            "incident",
            "root cause",
            "root-cause",
            "production support",
        ],
        "candidate_keywords": [
            "support",
            "supported",
            "troubleshooting",
            "debugging",
            "defect",
            "incident",
            "root cause",
            "root-cause",
            "investigated",
            "maintained",
        ],
    },
    "collaboration": {
        "job_keywords": [
            "collaborate",
            "collaborating",
            "collaboration",
            "cross functional",
            "cross-functional",
            "across teams",
            "stakeholder",
            "stakeholders",
            "team",
            "teams",
        ],
        "candidate_keywords": [
            "collaborated",
            "collaborate",
            "stakeholder",
            "stakeholders",
            "team",
            "teams",
            "testers",
            "application engineers",
            "product",
            "cross functional",
            "cross-functional",
        ],
    },
}


DOMAIN_CONCEPTS: dict[str, dict[str, list[str]]] = {
    "backend_software_engineering": {
        "job_keywords": [
            "backend",
            "back end",
            "software engineering",
            "software development",
            "application software",
            "api",
            "apis",
            "server side",
            "server-side",
        ],
        "candidate_keywords": [
            "backend",
            "back end",
            "software engineer",
            "software engineering",
            "software development",
            "application software",
            "full stack",
            "full stack engineering",
            "python",
            "java",
            "api",
            "apis",
            "fastapi",
            "flask",
            "spring",
            "service",
            "services",
        ],
    },
    "full_stack_engineering": {
        "job_keywords": [
            "full stack",
            "full-stack",
            "frontend and backend",
            "front end and back end",
            "web application",
            "web applications",
        ],
        "candidate_keywords": [
            "full stack",
            "full stack engineering",
            "full stack development",
            "react",
            "javascript",
            "typescript",
            "backend",
            "api",
            "apis",
            "web technologies",
        ],
    },
    "data_engineering": {
        "job_keywords": [
            "data engineering",
            "data integration",
            "data integrations",
            "data platform",
            "data platforms",
            "data pipeline",
            "data pipelines",
            "data intensive",
            "data-intensive",
            "etl",
            "database",
            "databases",
        ],
        "candidate_keywords": [
            "data engineering",
            "data pipeline",
            "data pipelines",
            "data intensive",
            "data-intensive",
            "sql",
            "postgresql",
            "database",
            "databases",
            "hpc",
            "etl",
            "data platform",
            "data platforms",
        ],
    },
    "cloud_engineering": {
        "job_keywords": [
            "cloud",
            "cloud engineering",
            "cloud based",
            "cloud-based",
            "aws",
            "gcp",
            "azure",
            "cloud platform",
            "cloud platforms",
        ],
        "candidate_keywords": [
            "cloud",
            "aws",
            "gcp",
            "azure",
            "deployment",
            "deployments",
            "ci cd",
            "ci/cd",
            "jenkins",
        ],
    },
    "ai_ml_software": {
        "job_keywords": [
            "ai",
            "ml",
            "artificial intelligence",
            "machine learning",
            "ai backed",
            "ai-backed",
            "llm",
            "model",
            "models",
        ],
        "candidate_keywords": [
            "ai",
            "ml",
            "machine learning",
            "artificial intelligence",
            "llm",
            "prompt engineering",
            "developer tooling",
            "ollama",
            "model",
            "models",
        ],
    },
    "scientific_technical_software": {
        "job_keywords": [
            "scientific software",
            "technical software",
            "simulation",
            "modelling",
            "modeling",
            "research software",
            "engineering software",
        ],
        "candidate_keywords": [
            "scientific software",
            "technical software",
            "simulation",
            "modelling",
            "modeling",
            "molecular dynamics",
            "quantum",
            "qm/mm",
            "hpc",
            "research",
        ],
    },
    "industrial_embedded_systems": {
        "job_keywords": [
            "industrial",
            "embedded",
            "machine",
            "manufacturing",
            "cnc",
            "systems software",
            "control systems",
        ],
        "candidate_keywords": [
            "industrial",
            "cnc",
            "machine",
            "manufacturing",
            "precision cnc",
            "systems",
            "application software",
            "production systems",
        ],
    },
}

SKILL_ALIASES: dict[str, list[str]] = {
    "software engineering": [
        "software engineer",
        "software engineering",
        "software development",
        "software developer",
        "application software",
        "application development",
        "full stack engineering",
        "full stack development",
        "backend engineering",
        "backend development",
        "systems development",
    ],
    "python": [
        "python",
        "pytest",
        "fastapi",
        "flask",
        "django",
    ],
    "ci cd": [
        "ci cd",
        "ci/cd",
        "jenkins",
        "github actions",
        "gitlab ci",
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
    ],
    "testing": [
        "testing",
        "test driven development",
        "tdd",
        "pytest",
        "junit",
        "mockito",
        "jest",
        "unit testing",
        "integration testing",
    ],
    "cloud": [
        "cloud",
        "aws",
        "gcp",
        "azure",
        "cloud based systems",
    ],
    "api": [
        "api",
        "apis",
        "rest",
        "rest api",
        "fastapi",
        "flask",
        "backend api",
        "api integration",
    ],
}


def calculate_match_score(
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
) -> MatchScoreCalculated:
    candidate_skill_evidence = build_candidate_skill_evidence(candidate_profile)

    required_skills = normalize_list(job_requirement.required_skills)
    preferred_skills = normalize_list(job_requirement.preferred_skills)

    matched_required_skills = get_matches(
        candidate_values=candidate_skill_evidence,
        required_values=job_requirement.required_skills,
    )

    matched_preferred_skills = get_matches(
        candidate_values=candidate_skill_evidence,
        required_values=job_requirement.preferred_skills,
    )

    missing_required_skills = get_missing(
        candidate_evidence=candidate_skill_evidence,
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

    candidate_domain_evidence = build_candidate_domain_evidence(candidate_profile)

    domain_score = calculate_domain_score(
        candidate_domain_evidence=candidate_domain_evidence,
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


def normalize_text(value: str | None) -> str:
    if not value:
        return ""

    return (
        value.strip()
        .lower()
        .replace("/", " ")
        .replace("-", " ")
        .replace("_", " ")
        .replace(",", " ")
    )


def normalize_list(values: list[str]) -> list[str]:
    return [normalize_text(value) for value in values if value.strip()]


def contains_any_keyword(text: str, keywords: list[str]) -> bool:
    normalized_text = normalize_text(text)

    return any(
        normalize_text(keyword) in normalized_text
        for keyword in keywords
    )


def candidate_has_concept(
    normalized_candidate_terms: list[str],
    candidate_keywords: list[str],
) -> bool:
    return any(
        contains_any_keyword(candidate_term, candidate_keywords)
        for candidate_term in normalized_candidate_terms
    )


def get_matches(candidate_values: list[str], required_values: list[str]) -> list[str]:
    matches: list[str] = []

    for required_value in required_values:
        if skill_matches(required_value, candidate_values):
            matches.append(required_value)

    return deduplicate_preserving_order(matches)


def get_missing(
    candidate_evidence: list[str],
    required_skills: list[str],
) -> list[str]:
    missing: list[str] = []

    for required_skill in required_skills:
        if not skill_matches(required_skill, candidate_evidence):
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
    candidate_domain_evidence: list[str],
    job_domain: str,
) -> int:
    max_score = 10

    if not job_domain:
        return 6

    normalized_job_domain = normalize_text(job_domain)
    normalized_candidate_evidence = normalize_list(candidate_domain_evidence)

    if not normalized_candidate_evidence:
        return 4

    # 1. Direct domain match
    for evidence in normalized_candidate_evidence:
        if (
            normalized_job_domain == evidence
            or normalized_job_domain in evidence
            or evidence in normalized_job_domain
        ):
            return max_score

    # 2. Concept-level adjacent domain match
    for concept in DOMAIN_CONCEPTS.values():
        job_has_concept = contains_any_keyword(
            normalized_job_domain,
            concept["job_keywords"],
        )

        candidate_has_matching_concept = candidate_has_concept(
            normalized_candidate_terms=normalized_candidate_evidence,
            candidate_keywords=concept["candidate_keywords"],
        )

        if job_has_concept and candidate_has_matching_concept:
            return 8

    # 3. Weak token overlap fallback
    job_tokens = tokenize(normalized_job_domain)

    if len(job_tokens) >= 2:
        for evidence in normalized_candidate_evidence:
            evidence_tokens = tokenize(evidence)
            overlap = job_tokens.intersection(evidence_tokens)

            if len(overlap) >= 2:
                return 7

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

    matches: list[str] = []

    for responsibility in job_responsibilities:
        normalized_responsibility = normalize_text(responsibility)

        direct_match = any(
            term in normalized_responsibility
            or normalized_responsibility in term
            for term in normalized_candidate_terms
        )

        concept_match = False

        for concept in RESPONSIBILITY_CONCEPTS.values():
            responsibility_has_concept = contains_any_keyword(
                normalized_responsibility,
                concept["job_keywords"],
            )

            candidate_has_matching_concept = candidate_has_concept(
                normalized_candidate_terms=normalized_candidate_terms,
                candidate_keywords=concept["candidate_keywords"],
            )

            if responsibility_has_concept and candidate_has_matching_concept:
                concept_match = True
                break

        if direct_match or concept_match:
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


def build_candidate_skill_evidence(candidate_profile: CandidateProfile) -> list[str]:
    evidence: list[str] = []

    evidence.extend(candidate_profile.core_skills or [])
    evidence.extend(candidate_profile.secondary_skills or [])
    evidence.extend(candidate_profile.target_roles or [])
    evidence.extend(candidate_profile.domains or [])

    for experience in candidate_profile.experience_summary or []:
        if isinstance(experience, dict):
            role = experience.get("role")
            summary = experience.get("summary")

            if role:
                evidence.append(str(role))

            if summary:
                evidence.append(str(summary))

    return evidence


def skill_matches(required_skill: str, candidate_evidence: list[str]) -> bool:
    normalized_required_skill = normalize_text(required_skill)

    if not normalized_required_skill:
        return False

    normalized_candidate_evidence = normalize_list(candidate_evidence)

    for candidate_value in normalized_candidate_evidence:
        if (
            normalized_required_skill == candidate_value
            or normalized_required_skill in candidate_value
            or candidate_value in normalized_required_skill
        ):
            return True

    required_options = split_grouped_skill_requirement(required_skill)

    if not required_options:
        required_options = [required_skill]

    for option in required_options:
        normalized_option = normalize_text(option)
        aliases = SKILL_ALIASES.get(normalized_option, [])

        for alias in aliases:
            normalized_alias = normalize_text(alias)

            if any(
                normalized_alias == candidate_value
                or normalized_alias in candidate_value
                or candidate_value in normalized_alias
                for candidate_value in normalized_candidate_evidence
            ):
                return True

    aliases = SKILL_ALIASES.get(normalized_required_skill, [])

    for alias in aliases:
        normalized_alias = normalize_text(alias)

        if any(
            normalized_alias == candidate_value
            or normalized_alias in candidate_value
            or candidate_value in normalized_alias
            for candidate_value in normalized_candidate_evidence
        ):
            return True

    return False


def build_candidate_domain_evidence(candidate_profile: CandidateProfile) -> list[str]:
    evidence: list[str] = []

    evidence.extend(candidate_profile.domains or [])
    evidence.extend(candidate_profile.core_skills or [])
    evidence.extend(candidate_profile.secondary_skills or [])
    evidence.extend(candidate_profile.target_roles or [])

    for experience in candidate_profile.experience_summary or []:
        if isinstance(experience, dict):
            company = experience.get("company")
            role = experience.get("role")
            summary = experience.get("summary")

            if company:
                evidence.append(str(company))

            if role:
                evidence.append(str(role))

            if summary:
                evidence.append(str(summary))

    return evidence


def tokenize(value: str | None) -> set[str]:
    normalized = normalize_text(value)
    return {token for token in normalized.split() if token}
