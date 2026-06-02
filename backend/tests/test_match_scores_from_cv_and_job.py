from fastapi.testclient import TestClient

from app.main import app

from app.core.database import SessionLocal
from app.schemas.candidate_profile import CandidateProfileExtracted
from app.schemas.cv_profile import CVProfileCreate
from app.schemas.job_listing import JobListingCreate
from app.schemas.job_requirements import JobRequirementsExtracted
from app.services.candidate_profile_service import upsert_candidate_profile
from app.services.cv_profile_service import create_cv_profile
from app.services.job_listing_service import create_job_listing
from app.services.job_requirement_service import upsert_job_requirement


client = TestClient(app)


def test_create_match_score_from_cv_and_job_returns_400_when_extracted_data_missing():
    cv_response = client.post(
        "/cv-profiles",
        json={
            "filename": "test_cv.txt",
            "raw_text": "Experienced software engineer with Java and Python.",
        },
    )

    assert cv_response.status_code in [200, 201]
    cv_profile_id = cv_response.json()["id"]

    job_response = client.post(
        "/job-listings",
        json={
            "title": "Senior Software Engineer",
            "company": "Test Company",
            "location": "Melbourne VIC",
            "source": "manual",
            "url": "https://example.com/jobs/senior-software-engineer",
            "raw_description": "We need Java, Python, APIs, and backend engineering.",
        },
    )


    assert job_response.status_code in [200, 201]
    job_listing_id = job_response.json()["id"]

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": cv_profile_id,
            "job_listing_id": job_listing_id,
            "auto_extract_missing": False,
        },
    )

    assert response.status_code == 400

    body = response.json()
    assert "detail" in body
    assert "candidate_profile" in str(body["detail"])
    assert "job_requirement" in str(body["detail"])


def test_create_match_score_from_cv_and_job_returns_404_when_cv_profile_missing():
    job_response = client.post(
        "/job-listings",
        json={
            "title": "Senior Software Engineer",
            "company": "Test Company",
            "location": "Melbourne VIC",
            "source": "manual",
            "url": "https://example.com/jobs/senior-software-engineer-missing-cv-test",
            "raw_description": "We need Java and Python.",
        },
    )

    assert job_response.status_code in [200, 201]
    job_listing_id = job_response.json()["id"]

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": "missing-cv-profile-id",
            "job_listing_id": job_listing_id,
            "auto_extract_missing": False,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "CV profile not found"


def test_create_match_score_from_cv_and_job_returns_404_when_job_listing_missing():
    cv_response = client.post(
        "/cv-profiles",
        json={
            "filename": "test_cv.txt",
            "raw_text": "Experienced software engineer with Java and Python.",
        },
    )

    assert cv_response.status_code in [200, 201]
    cv_profile_id = cv_response.json()["id"]

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": cv_profile_id,
            "job_listing_id": "missing-job-listing-id",
            "auto_extract_missing": False,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job listing not found"


def test_create_match_score_from_cv_and_job_returns_score_when_extracted_data_exists():
    db = SessionLocal()

    try:
        cv_profile = create_cv_profile(
            db,
            CVProfileCreate(
                filename="from_cv_job_match_test_cv.txt",
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
                url="https://example.com/jobs/from-cv-job-senior-backend-developer",
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

        cv_profile_id = cv_profile.id
        job_listing_id = job_listing.id
        candidate_profile_id = candidate_profile.id
        job_requirement_id = job_requirement.id

    finally:
        db.close()

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": cv_profile_id,
            "job_listing_id": job_listing_id,
            "auto_extract_missing": False,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["candidate_profile_id"] == candidate_profile_id
    assert data["job_requirement_id"] == job_requirement_id
    assert data["total_score"] >= 70
    assert data["recommendation"] in ["Apply", "Maybe"]


def test_create_match_score_from_cv_and_job_auto_extracts_missing_data(monkeypatch):
    def fake_extract_candidate_profile_from_cv(raw_text):
        return CandidateProfileExtracted(
            target_roles=["Senior Backend Developer"],
            core_skills=["Python", "FastAPI", "PostgreSQL"],
            secondary_skills=["AWS"],
            seniority="Senior",
            domains=["backend software engineering"],
            location_preferences=["Melbourne VIC"],
        )

    def fake_extract_job_requirements_from_listing(
        title,
        company,
        location,
        raw_description,
    ):
        return JobRequirementsExtracted(
            required_skills=["Python", "FastAPI"],
            preferred_skills=["AWS"],
            responsibilities=["build backend APIs"],
            seniority="Senior",
            domain="backend software engineering",
            work_arrangement="Hybrid",
            location="Melbourne VIC",
        )

    monkeypatch.setattr(
        "app.api.match_scores.extract_candidate_profile_from_cv",
        fake_extract_candidate_profile_from_cv,
    )

    monkeypatch.setattr(
        "app.api.match_scores.extract_job_requirements_from_listing",
        fake_extract_job_requirements_from_listing,
    )

    cv_response = client.post(
        "/cv-profiles",
        json={
            "filename": "auto_extract_test_cv.txt",
            "raw_text": "Senior Backend Developer with Python and FastAPI.",
        },
    )

    assert cv_response.status_code in [200, 201]
    cv_profile_id = cv_response.json()["id"]

    job_response = client.post(
        "/job-listings",
        json={
            "title": "Senior Backend Developer",
            "company": "Example Company",
            "location": "Melbourne VIC",
            "source": "manual",
            "url": "https://example.com/jobs/auto-extract-senior-backend-developer",
            "raw_description": "Senior backend role requiring Python and FastAPI.",
        },
    )

    assert job_response.status_code in [200, 201]
    job_listing_id = job_response.json()["id"]

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": cv_profile_id,
            "job_listing_id": job_listing_id,
            "auto_extract_missing": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["candidate_profile_id"]
    assert data["job_requirement_id"]
    assert data["total_score"] >= 70
    assert data["recommendation"] in ["Apply", "Maybe"]
