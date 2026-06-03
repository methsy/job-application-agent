from fastapi.testclient import TestClient
from datetime import datetime, UTC
from uuid import uuid4

from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.models.match_score import MatchScore
from app.services.application_advice_service import generate_application_advice
from app.services.tailored_cv_draft_service import generate_tailored_cv_draft
from app.main import app

client = TestClient(app)


def test_generate_tailored_cv_draft_returns_backend_api_cv_draft():
    candidate_profile, job_requirement, match_score = _build_test_objects()

    application_advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    draft = generate_tailored_cv_draft(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
        application_advice=application_advice,
    )

    assert draft.cv_angle
    assert draft.target_headline == "Backend/API Software Engineer"
    assert "Python" in draft.skills_to_emphasise
    assert "CI/CD" in draft.skills_to_emphasise
    assert "Backend API design, implementation, and integration" in draft.experience_themes
    assert "Professional Summary" in draft.draft_text
    assert "Skills to Emphasise" in draft.draft_text
    assert "ATS Keywords to Include Where Truthful" in draft.draft_text


def test_generate_tailored_cv_draft_includes_risk_notes_from_application_advice():
    candidate_profile, job_requirement, match_score = _build_test_objects(
        gaps=[
            "Nice-to-have: ml/aI frameworks",
            "Nice-to-have: ci/cd",
            "Nice-to-have: scalable system design",
        ]
    )

    application_advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    draft = generate_tailored_cv_draft(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
        application_advice=application_advice,
    )

    assert "Clarify depth of hands-on ML/AI framework experience." in draft.risk_notes
    assert "Mention nice-to-have requirements only where truthful." in draft.risk_notes
    assert "Review Before Using" in draft.draft_text


def _build_test_objects(gaps: list[str] | None = None):
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
            "API integration",
            "testing",
            "automation",
            "production delivery",
        ],
        gaps=gaps or [],
        reasoning_summary="Score 82/100. Recommendation: Apply.",
        created_at=now,
    )

    return candidate_profile, job_requirement, match_score


def test_get_tailored_cv_draft_returns_404_for_missing_match_score():
    response = client.get(
        "/match-scores/00000000-0000-0000-0000-000000000000/tailored-cv-draft"
    )

    assert response.status_code == 404
