from app.schemas.candidate_profile import CandidateProfileExtracted
from app.schemas.cv_profile import CVProfileCreate
from app.services.candidate_profile_service import (
    get_candidate_profile_by_cv_profile_id,
    upsert_candidate_profile,
)
from app.services.cv_profile_service import create_cv_profile
from app.core.database import SessionLocal


def test_upsert_candidate_profile_creates_profile():
    db = SessionLocal()

    try:
        cv_profile = create_cv_profile(
            db,
            CVProfileCreate(
                filename="candidate_profile_test_cv.txt",
                raw_text="Senior Software Engineer with Java and Python.",
            ),
        )

        extracted_profile = CandidateProfileExtracted(
            target_roles=["Senior Software Engineer"],
            core_skills=["Java", "Python"],
            seniority="Senior",
            domains=["software engineering"],
        )

        candidate_profile = upsert_candidate_profile(
            db=db,
            cv_profile_id=cv_profile.id,
            extracted_profile=extracted_profile,
        )

        assert candidate_profile.id
        assert candidate_profile.cv_profile_id == cv_profile.id
        assert candidate_profile.target_roles == ["Senior Software Engineer"]
        assert candidate_profile.core_skills == ["Java", "Python"]
    finally:
        db.close()


def test_upsert_candidate_profile_updates_existing_profile():
    db = SessionLocal()

    try:
        cv_profile = create_cv_profile(
            db,
            CVProfileCreate(
                filename="candidate_profile_update_test_cv.txt",
                raw_text="Backend Developer with FastAPI.",
            ),
        )

        first_profile = CandidateProfileExtracted(
            target_roles=["Backend Developer"],
            core_skills=["FastAPI"],
            seniority="Mid",
        )

        second_profile = CandidateProfileExtracted(
            target_roles=["Senior Backend Developer"],
            core_skills=["FastAPI", "PostgreSQL"],
            seniority="Senior",
        )

        created_profile = upsert_candidate_profile(
            db=db,
            cv_profile_id=cv_profile.id,
            extracted_profile=first_profile,
        )

        updated_profile = upsert_candidate_profile(
            db=db,
            cv_profile_id=cv_profile.id,
            extracted_profile=second_profile,
        )

        assert updated_profile.id == created_profile.id
        assert updated_profile.target_roles == ["Senior Backend Developer"]
        assert updated_profile.core_skills == ["FastAPI", "PostgreSQL"]
        assert updated_profile.seniority == "Senior"
    finally:
        db.close()


def test_get_candidate_profile_by_cv_profile_id_returns_profile():
    db = SessionLocal()

    try:
        cv_profile = create_cv_profile(
            db,
            CVProfileCreate(
                filename="candidate_profile_get_test_cv.txt",
                raw_text="Python developer.",
            ),
        )

        extracted_profile = CandidateProfileExtracted(
            target_roles=["Python Developer"],
            core_skills=["Python"],
        )

        created_profile = upsert_candidate_profile(
            db=db,
            cv_profile_id=cv_profile.id,
            extracted_profile=extracted_profile,
        )

        fetched_profile = get_candidate_profile_by_cv_profile_id(
            db=db,
            cv_profile_id=cv_profile.id,
        )

        assert fetched_profile is not None
        assert fetched_profile.id == created_profile.id
    finally:
        db.close()
