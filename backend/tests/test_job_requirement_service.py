from app.core.database import SessionLocal
from app.schemas.job_listing import JobListingCreate
from app.schemas.job_requirements import JobRequirementsExtracted
from app.services.job_listing_service import create_job_listing
from app.services.job_requirement_service import (
    get_job_requirement_by_job_listing_id,
    upsert_job_requirement,
)


def test_upsert_job_requirement_creates_requirement():
    db = SessionLocal()

    try:
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

        extracted_requirements = JobRequirementsExtracted(
            required_skills=["Python", "FastAPI"],
            preferred_skills=["AWS"],
            responsibilities=["build backend APIs"],
            seniority="Senior",
            domain="backend software engineering",
            work_arrangement="Hybrid",
            location="Melbourne VIC",
            keywords_for_ats=["Python", "FastAPI", "AWS"],
        )

        job_requirement = upsert_job_requirement(
            db=db,
            job_listing_id=job_listing.id,
            extracted_requirements=extracted_requirements,
        )

        assert job_requirement.id
        assert job_requirement.job_listing_id == job_listing.id
        assert job_requirement.required_skills == ["Python", "FastAPI"]
        assert job_requirement.preferred_skills == ["AWS"]
        assert job_requirement.seniority == "Senior"
    finally:
        db.close()


def test_upsert_job_requirement_updates_existing_requirement():
    db = SessionLocal()

    try:
        job_listing = create_job_listing(
            db,
            JobListingCreate(
                title="Backend Developer",
                company="Another Company",
                location="Remote Australia",
                source="manual",
                url="https://example.com/jobs/backend-developer",
                raw_description="Backend role requiring FastAPI.",
            ),
        )

        first_requirements = JobRequirementsExtracted(
            required_skills=["FastAPI"],
            seniority="Mid",
        )

        second_requirements = JobRequirementsExtracted(
            required_skills=["FastAPI", "PostgreSQL"],
            preferred_skills=["Docker"],
            seniority="Senior",
        )

        created_requirement = upsert_job_requirement(
            db=db,
            job_listing_id=job_listing.id,
            extracted_requirements=first_requirements,
        )

        updated_requirement = upsert_job_requirement(
            db=db,
            job_listing_id=job_listing.id,
            extracted_requirements=second_requirements,
        )

        assert updated_requirement.id == created_requirement.id
        assert updated_requirement.required_skills == ["FastAPI", "PostgreSQL"]
        assert updated_requirement.preferred_skills == ["Docker"]
        assert updated_requirement.seniority == "Senior"
    finally:
        db.close()


def test_get_job_requirement_by_job_listing_id_returns_requirement():
    db = SessionLocal()

    try:
        job_listing = create_job_listing(
            db,
            JobListingCreate(
                title="Python Developer",
                company="Test Company",
                location="Melbourne VIC",
                source="manual",
                url="https://example.com/jobs/python-developer",
                raw_description="Python developer role.",
            ),
        )

        extracted_requirements = JobRequirementsExtracted(
            required_skills=["Python"],
            responsibilities=["develop backend services"],
        )

        created_requirement = upsert_job_requirement(
            db=db,
            job_listing_id=job_listing.id,
            extracted_requirements=extracted_requirements,
        )

        fetched_requirement = get_job_requirement_by_job_listing_id(
            db=db,
            job_listing_id=job_listing.id,
        )

        assert fetched_requirement is not None
        assert fetched_requirement.id == created_requirement.id
    finally:
        db.close()
