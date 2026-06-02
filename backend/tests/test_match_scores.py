from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.schemas.candidate_profile import CandidateProfileExtracted
from app.schemas.cv_profile import CVProfileCreate
from app.schemas.job_listing import JobListingCreate
from app.schemas.job_requirements import JobRequirementsExtracted
from app.services.candidate_profile_service import upsert_candidate_profile
from app.services.cv_profile_service import create_cv_profile
from app.services.job_listing_service import create_job_listing
from app.services.job_requirement_service import upsert_job_requirement

client = TestClient(app)


def test_create_match_score():
    db = SessionLocal()

    try:
        cv_profile = create_cv_profile(
            db,
            CVProfileCreate(
                filename="match_test_cv.txt",
                raw_text="Senior Backend Developer with Python and FastAPI.",
            ),
        )

        candidate_profile = upsert_candidate_profile(
            db=db,
            cv_profile_id=cv_profile.id,
            extracted_profile=CandidateProfileExtracted(
                target_roles=["Senior Backend Developer"],
                core_skills=["Python", "FastAPI", "PostgreSQL"],
                secondary_skills=["AWS"],
                seniority="Senior",
                domains=["backend software engineering"],
                location_preferences=["Melbourne VIC"],
            ),
        )

        job_listing = create_job_listing(
            db,
            JobListingCreate(
                title="Senior Backend Developer",
                company="Example Company",
                location="Melbourne VIC",
                source="manual",
                url="https://example.com/jobs/senior-backend-developer",
                raw_description="Senior backend role requiring Python and FastAPI.",
            ),
        )

        job_requirement = upsert_job_requirement(
            db=db,
            job_listing_id=job_listing.id,
            extracted_requirements=JobRequirementsExtracted(
                required_skills=["Python", "FastAPI"],
                preferred_skills=["AWS"],
                responsibilities=["build backend APIs"],
                seniority="Senior",
                domain="backend software engineering",
                work_arrangement="Hybrid",
                location="Melbourne VIC",
            ),
        )
        candidate_profile_id = candidate_profile.id
        job_requirement_id = job_requirement.id

    finally:
        db.close()

    response = client.post(
        "/match-scores",
        json={
            "candidate_profile_id": candidate_profile_id,
            "job_requirement_id": job_requirement_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["candidate_profile_id"] == candidate_profile_id
    assert data["job_requirement_id"] == job_requirement_id
    assert data["total_score"] >= 70
    assert data["recommendation"] in ["Apply", "Maybe"]


def test_list_match_scores():
    response = client.get("/match-scores")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_match_score_returns_404_for_missing_id():
    response = client.get("/match-scores/non-existent-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Match score not found"}


def test_create_match_score_returns_404_for_missing_candidate_profile():
    response = client.post(
        "/match-scores",
        json={
            "candidate_profile_id": "missing-candidate-profile",
            "job_requirement_id": "missing-job-requirement",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Candidate profile not found"}
