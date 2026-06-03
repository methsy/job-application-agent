from datetime import datetime, UTC
from uuid import uuid4

from app.schemas.candidate_profile import CandidateProfileRead
from app.schemas.job_requirements import JobRequirementRead
from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.services.match_scoring_service import (
    HARD_REQUIREMENT_NEEDS_REVIEW,
    HARD_REQUIREMENT_SATISFIED,
    calculate_constraints_score,
    calculate_match_score,
    calculate_domain_score,
    interpret_hard_requirement,
    match_responsibilities,
    skill_matches,
)



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


def test_match_responsibilities_matches_data_engineering_concept():
    matched = match_responsibilities(
        candidate_domains=[],
        candidate_skills=[
            "Data Pipelines & Data-Intensive Systems",
            "SQL (PostgreSQL)",
        ],
        candidate_target_roles=[],
        candidate_experience_summaries=[],
        job_responsibilities=[
            "working with data integrations",
        ],
    )

    assert "working with data integrations" in matched


def test_match_responsibilities_matches_api_and_cloud_concepts():
    matched = match_responsibilities(
        candidate_domains=[],
        candidate_skills=[
            "Python",
            "Full Stack Engineering",
            "AWS",
            "GCP",
        ],
        candidate_target_roles=[],
        candidate_experience_summaries=[],
        job_responsibilities=[
            "integrating APIs and cloud-based systems",
        ],
    )

    assert "integrating APIs and cloud-based systems" in matched


def test_match_responsibilities_matches_ai_ml_concept():
    matched = match_responsibilities(
        candidate_domains=[],
        candidate_skills=[
            "Machine Learning",
            "AI & Developer Tooling",
            "LLM task extraction",
            "prompt engineering",
        ],
        candidate_target_roles=[],
        candidate_experience_summaries=[],
        job_responsibilities=[
            "designing and delivering AI-backed software solutions",
        ],
    )

    assert "designing and delivering AI-backed software solutions" in matched


def test_match_responsibilities_does_not_match_unrelated_responsibility():
    matched = match_responsibilities(
        candidate_domains=[],
        candidate_skills=[
            "Python",
            "PostgreSQL",
        ],
        candidate_target_roles=[],
        candidate_experience_summaries=[],
        job_responsibilities=[
            "leading enterprise sales strategy",
        ],
    )

    assert matched == []


def test_match_responsibilities_matches_current_ai_python_job_responsibilities():
    matched = match_responsibilities(
        candidate_domains=[],
        candidate_skills=[
            "Python",
            "Full Stack Engineering",
            "Data Pipelines & Data-Intensive Systems",
            "SQL (PostgreSQL)",
            "AWS",
            "GCP",
            "Machine Learning",
            "CI/CD pipelines",
            "Jenkins",
            "Test Driven Development",
            "AI & Developer Tooling",
            "LLM task extraction",
            "prompt engineering",
        ],
        candidate_target_roles=[],
        candidate_experience_summaries=[
            {
                "company": "ANCA CNC Machines",
                "role": "Software Engineer",
                "summary": "Developed and supported high-performance application software for production CNC systems.",
            }
        ],
        job_responsibilities=[
            "designing and delivering AI-backed software solutions",
            "collaborating across teams to solve meaningful problems",
            "moving from prototype to production",
            "working with data integrations",
            "integrating APIs and cloud-based systems",
        ],
    )

    assert "designing and delivering AI-backed software solutions" in matched
    assert "moving from prototype to production" in matched
    assert "working with data integrations" in matched
    assert "integrating APIs and cloud-based systems" in matched


def test_calculate_domain_score_matches_backend_software_engineering_evidence():
    score = calculate_domain_score(
        candidate_domain_evidence=[
            "Full Stack Engineering",
            "Software Engineer",
            "Python",
            "Application software development",
        ],
        job_domain="backend software engineering",
    )

    assert score >= 8


def test_calculate_domain_score_matches_data_engineering_evidence():
    score = calculate_domain_score(
        candidate_domain_evidence=[
            "Data Pipelines & Data-Intensive Systems",
            "SQL (PostgreSQL)",
            "HPC environments",
        ],
        job_domain="data engineering",
    )

    assert score >= 8


def test_calculate_domain_score_matches_ai_ml_software_evidence():
    score = calculate_domain_score(
        candidate_domain_evidence=[
            "Machine Learning",
            "AI & Developer Tooling",
            "LLM task extraction",
            "prompt engineering",
        ],
        job_domain="AI software engineering",
    )

    assert score >= 8


def test_calculate_domain_score_returns_low_score_for_unrelated_domain():
    score = calculate_domain_score(
        candidate_domain_evidence=[
            "Python",
            "PostgreSQL",
        ],
        job_domain="enterprise sales strategy",
    )

    assert score == 4


def test_interpret_hard_requirement_satisfies_software_engineering_experience():
    result = interpret_hard_requirement(
        hard_requirement="mandatory 3-5 years hands-on experience in software engineering",
        candidate_evidence=[
            "Software Engineer",
            "Full Stack Engineering",
            "Developed and supported application software for production systems",
            "Python",
            "Java",
        ],
    )

    assert result == HARD_REQUIREMENT_SATISFIED


def test_interpret_hard_requirement_satisfies_cloud_experience():
    result = interpret_hard_requirement(
        hard_requirement="must have cloud experience",
        candidate_evidence=[
            "AWS",
            "GCP",
            "CI/CD pipelines",
        ],
    )

    assert result == HARD_REQUIREMENT_SATISFIED


def test_interpret_hard_requirement_keeps_citizenship_as_review_without_explicit_evidence():
    result = interpret_hard_requirement(
        hard_requirement="must be an Australian citizen",
        candidate_evidence=[
            "Software Engineer",
            "Python",
            "AWS",
        ],
    )

    assert result == HARD_REQUIREMENT_NEEDS_REVIEW


def test_calculate_constraints_score_full_when_all_hard_requirements_satisfied():
    score = calculate_constraints_score(
        hard_requirement_results={
            "mandatory 3-5 years hands-on experience in software engineering": HARD_REQUIREMENT_SATISFIED,
        }
    )

    assert score == 5


def test_calculate_constraints_score_partial_when_hard_requirements_need_review():
    score = calculate_constraints_score(
        hard_requirement_results={
            "must be an Australian citizen": HARD_REQUIREMENT_NEEDS_REVIEW,
        }
    )

    assert score == 2
