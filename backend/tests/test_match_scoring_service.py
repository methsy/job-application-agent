from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.services.match_scoring_service import calculate_match_score


def test_calculate_match_score_for_strong_match():
    candidate_profile = CandidateProfile(
        cv_profile_id="cv-1",
        target_roles=["Senior Backend Developer"],
        core_skills=["Python", "FastAPI", "PostgreSQL", "REST APIs", "unit testing"],
        secondary_skills=["AWS", "Docker"],
        seniority="Senior",
        domains=["backend software engineering", "production support", "data workflows"],
        location_preferences=["Melbourne VIC"],
        work_arrangement_preferences=["Hybrid"],
    )

    job_requirement = JobRequirement(
        job_listing_id="job-1",
        required_skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
            "REST APIs",
            "unit testing",
        ],
        preferred_skills=["AWS", "Docker", "CI/CD"],
        responsibilities=[
            "design backend APIs",
            "build backend APIs",
            "support backend APIs",
            "support data workflows",
        ],
        seniority="Senior",
        domain="backend software engineering",
        employment_type="Full-time",
        work_arrangement="Hybrid",
        location="Melbourne VIC",
        hard_requirements=[],
        keywords_for_ats=["Python", "FastAPI", "PostgreSQL"],
    )

    result = calculate_match_score(
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    assert result.total_score >= 75
    assert result.recommendation == "Apply"
    assert "Python" in result.matched_skills
    assert "FastAPI" in result.matched_skills
    assert result.missing_required_skills == []


def test_calculate_match_score_for_weak_match():
    candidate_profile = CandidateProfile(
        cv_profile_id="cv-2",
        target_roles=["Backend Developer"],
        core_skills=["Python"],
        secondary_skills=[],
        seniority="Junior",
        domains=["scripting"],
        location_preferences=["Melbourne VIC"],
    )

    job_requirement = JobRequirement(
        job_listing_id="job-2",
        required_skills=[
            "Java",
            "Spring Boot",
            "Kubernetes",
            "Kafka",
        ],
        preferred_skills=["AWS"],
        responsibilities=["design distributed systems"],
        seniority="Senior",
        domain="enterprise backend engineering",
        work_arrangement="Onsite",
        location="Sydney NSW",
        hard_requirements=[],
    )

    result = calculate_match_score(
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    assert result.total_score < 55
    assert result.recommendation == "Skip"
    assert "Java" in result.missing_required_skills


def test_calculate_match_score_matches_grouped_alternative_skill_requirement():
    candidate_profile = CandidateProfile(
        cv_profile_id="cv-3",
        target_roles=["Senior Software Engineer"],
        core_skills=["Java", "Python"],
        secondary_skills=["SQL"],
        seniority="Senior",
        domains=["software engineering", "backend software engineering"],
        location_preferences=["Melbourne"],
    )

    job_requirement = JobRequirement(
        job_listing_id="job-3",
        required_skills=[
            "at least one of NET/C#, Java, Python, JavaScript, or TypeScript",
            "API design",
        ],
        preferred_skills=[],
        responsibilities=["design and build scalable software applications"],
        seniority="Senior",
        domain="software engineering",
        work_arrangement="Hybrid",
        location="Melbourne",
        hard_requirements=[],
    )

    result = calculate_match_score(
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    assert (
        "at least one of NET/C#, Java, Python, JavaScript, or TypeScript"
        in result.matched_skills
    )
    assert (
        "at least one of NET/C#, Java, Python, JavaScript, or TypeScript"
        not in result.missing_required_skills
    )
    assert result.technical_skill_score > 0
