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
