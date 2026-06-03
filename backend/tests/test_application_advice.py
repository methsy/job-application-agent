from fastapi.testclient import TestClient
from datetime import datetime, UTC
from uuid import uuid4

from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.models.match_score import MatchScore
from app.services.application_advice_service import generate_application_advice
from app.main import app

client = TestClient(app)


def test_generate_application_advice_returns_apply_decision():
    now = datetime.now(UTC)

    candidate_profile = CandidateProfile(
        id=str(uuid4()),
        cv_profile_id=str(uuid4()),
        target_roles=["Backend Developer"],
        core_skills=["Python", "FastAPI", "PostgreSQL", "AWS"],
        secondary_skills=["CI/CD", "Testing"],
        seniority="Senior",
        domains=["backend software engineering"],
        experience_summary=[],
        location_preferences=[],
        work_arrangement_preferences=[],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    job_requirement = JobRequirement(
        id=str(uuid4()),
        job_listing_id=str(uuid4()),
        required_skills=["python", "software engineering"],
        preferred_skills=["ci/cd", "testing"],
        responsibilities=[
            "building backend APIs",
            "moving from prototype to production",
        ],
        seniority="",
        domain="backend software engineering",
        employment_type="",
        work_arrangement="",
        location="",
        salary_range="",
        application_deadline="",
        hard_requirements=[],
        nice_to_have=[],
        keywords_for_ats=["python developer", "backend APIs"],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    match_score = MatchScore(
        id=str(uuid4()),
        candidate_profile_id=candidate_profile.id,
        job_requirement_id=job_requirement.id,
        total_score=82,
        technical_skill_score=32,
        responsibility_score=18,
        seniority_score=10,
        domain_score=8,
        location_score=7,
        constraints_score=5,
        career_strategy_score=5,
        recommendation="Apply",
        matched_skills=["python", "software engineering"],
        missing_required_skills=[],
        matched_preferred_skills=["ci/cd", "testing"],
        matched_responsibilities=[
            "building backend APIs",
            "moving from prototype to production",
        ],
        gaps=[],
        reasoning_summary="Score 82/100. Recommendation: Apply.",
        created_at=now,
    )

    advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    assert advice.decision == "Apply"
    assert "Python" in advice.keywords_to_add or "python" in advice.keywords_to_add
    assert advice.best_cv_angle
    assert advice.cover_letter_angle
    assert advice.next_action


def test_generate_application_advice_returns_review_decision_for_review_score():
    now = datetime.now(UTC)

    candidate_profile = CandidateProfile(
        id=str(uuid4()),
        cv_profile_id=str(uuid4()),
        target_roles=[],
        core_skills=["Python"],
        secondary_skills=[],
        seniority="",
        domains=[],
        experience_summary=[],
        location_preferences=[],
        work_arrangement_preferences=[],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    job_requirement = JobRequirement(
        id=str(uuid4()),
        job_listing_id=str(uuid4()),
        required_skills=["python", "cloud"],
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
        keywords_for_ats=["python"],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    match_score = MatchScore(
        id=str(uuid4()),
        candidate_profile_id=candidate_profile.id,
        job_requirement_id=job_requirement.id,
        total_score=62,
        technical_skill_score=20,
        responsibility_score=10,
        seniority_score=8,
        domain_score=6,
        location_score=7,
        constraints_score=5,
        career_strategy_score=3,
        recommendation="Review",
        matched_skills=["python"],
        missing_required_skills=["cloud"],
        matched_preferred_skills=[],
        matched_responsibilities=[],
        gaps=["Missing required skill: cloud"],
        reasoning_summary="Score 62/100. Recommendation: Review.",
        created_at=now,
    )

    advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    assert advice.decision == "Review"
    assert any("cloud" in note.lower() for note in advice.risk_notes)


def test_get_application_advice_returns_404_for_missing_match_score():
    response = client.get(
        "/match-scores/00000000-0000-0000-0000-000000000000/application-advice"
    )

    assert response.status_code == 404


def test_application_advice_formats_keywords_for_display():
    candidate_profile, job_requirement, match_score = _build_application_advice_test_objects(
        matched_skills=["python", "software engineering"],
        matched_responsibilities=["testing", "automation"],
        gaps=["Nice-to-have: ml/aI frameworks", "Nice-to-have: ci/cd"],
        recommendation="Apply",
    )

    advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    assert "Python" in advice.keywords_to_add
    assert "CI/CD" in advice.keywords_to_add
    assert "ML/AI frameworks" in advice.keywords_to_add

    assert "python" not in advice.keywords_to_add
    assert "ci/cd" not in advice.keywords_to_add
    assert "ml/aI frameworks" not in advice.keywords_to_add


def test_application_advice_generates_natural_cover_letter_angle():
    candidate_profile, job_requirement, match_score = _build_application_advice_test_objects(
        matched_skills=["python", "software engineering"],
        matched_responsibilities=[
            "API integration",
            "testing",
            "automation",
            "production delivery",
        ],
        gaps=["Nice-to-have: ci/cd"],
        recommendation="Apply",
    )

    advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    cover_letter_angle = advice.cover_letter_angle

    assert "Position the application around" in cover_letter_angle
    assert "evidence that matches" not in cover_letter_angle
    assert "Python" in cover_letter_angle or "backend/API software engineering" in cover_letter_angle
    assert "testing" in cover_letter_angle


def test_application_advice_generates_specific_risk_notes():
    candidate_profile, job_requirement, match_score = _build_application_advice_test_objects(
        matched_skills=["python"],
        matched_responsibilities=["testing", "automation"],
        gaps=[
            "Nice-to-have: ml/aI frameworks",
            "Nice-to-have: ci/cd",
            "Nice-to-have: scalable system design",
        ],
        recommendation="Apply",
    )

    advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    risk_notes = advice.risk_notes

    assert "Clarify depth of hands-on ML/AI framework experience." in risk_notes
    assert "Emphasise CI/CD, testing, automation, and quality engineering examples." in risk_notes
    assert "Use concrete examples of scalable system design or architecture decisions." in risk_notes
    assert "Mention nice-to-have requirements only where truthful." in risk_notes


def _build_application_advice_test_objects(
    matched_skills: list[str],
    matched_responsibilities: list[str],
    gaps: list[str],
    recommendation: str,
    missing_required_skills: list[str] | None = None,
):
    now = datetime.now(UTC)

    candidate_profile = CandidateProfile(
        id=str(uuid4()),
        cv_profile_id=str(uuid4()),
        target_roles=["Backend Developer"],
        core_skills=["Python", "FastAPI", "PostgreSQL", "AWS"],
        secondary_skills=["CI/CD", "Testing", "Automation"],
        seniority="Senior",
        domains=["backend software engineering"],
        experience_summary=[],
        location_preferences=[],
        work_arrangement_preferences=[],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    job_requirement = JobRequirement(
        id=str(uuid4()),
        job_listing_id=str(uuid4()),
        required_skills=["python", "software engineering"],
        preferred_skills=[
            "ci/cd",
            "testing",
            "automation",
            "ml/aI frameworks",
            "scalable system design",
        ],
        responsibilities=[
            "API integration",
            "testing",
            "automation",
            "production delivery",
            "scalable system design",
        ],
        seniority="",
        domain="backend software engineering",
        employment_type="",
        work_arrangement="",
        location="",
        salary_range="",
        application_deadline="",
        hard_requirements=[],
        nice_to_have=[
            "ml/aI frameworks",
            "ci/cd",
            "scalable system design",
        ],
        keywords_for_ats=[
            "python",
            "software engineering",
            "ml/aI frameworks",
            "ci/cd",
            "automation",
            "testing",
            "scalable system design",
            "python developer",
        ],
        extraction_notes="",
        created_at=now,
        updated_at=now,
    )

    match_score = MatchScore(
        id=str(uuid4()),
        candidate_profile_id=candidate_profile.id,
        job_requirement_id=job_requirement.id,
        total_score=78,
        technical_skill_score=28,
        responsibility_score=16,
        seniority_score=12,
        domain_score=8,
        location_score=8,
        constraints_score=3,
        career_strategy_score=3,
        recommendation=recommendation,
        matched_skills=matched_skills,
        missing_required_skills=missing_required_skills or [],
        matched_preferred_skills=["ci/cd", "testing"],
        matched_responsibilities=matched_responsibilities,
        gaps=gaps,
        reasoning_summary="Test score for application advice wording.",
        created_at=now,
    )

    return candidate_profile, job_requirement, match_score
