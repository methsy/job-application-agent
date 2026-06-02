from datetime import datetime, UTC
from uuid import uuid4

from app.schemas.candidate_profile import CandidateProfileRead
from app.schemas.job_requirements import JobRequirementRead
from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.services.match_scoring_service import calculate_match_score
from app.services.match_scoring_service import skill_matches


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


def test_software_engineering_requirement_matches_software_engineer_experience():
    now = datetime.now(UTC)

    candidate_profile = CandidateProfileRead(
        id=str(uuid4()),
        cv_profile_id=str(uuid4()),
        target_roles=[],
        core_skills=[
            "Python",
            "Full Stack Engineering",
            "AWS",
        ],
        secondary_skills=[],
        seniority="",
        domains=[],
        experience_summary=[
            {
                "company": "ANCA CNC Machines",
                "role": "Software Engineer",
                "summary": "Developed and supported application software for precision CNC systems.",
            }
        ],
        location_preferences=[],
        work_arrangement_preferences=[],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    job_requirement = JobRequirementRead(
        id=str(uuid4()),
        job_listing_id=str(uuid4()),
        required_skills=[
            "python",
            "software engineering",
        ],
        preferred_skills=[],
        responsibilities=[],
        seniority="",
        domain="backend software engineering",
        employment_type="",
        work_arrangement="",
        location="",
        salary_range="",
        application_deadline="",
        hard_requirements=[],
        nice_to_have=[],
        keywords_for_ats=[],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    result = calculate_match_score(candidate_profile, job_requirement)

    assert "python" in result.matched_skills
    assert "software engineering" in result.matched_skills
    assert "software engineering" not in result.missing_required_skills

def test_skill_matches_software_engineering_to_full_stack_engineering():
    candidate_evidence = [
        "Python",
        "Full Stack Engineering",
        "Software Engineer",
        "Developed and supported application software",
    ]

    assert skill_matches("software engineering", candidate_evidence) is True
