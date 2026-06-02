from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_listing import JobListing
from app.schemas.job_listing import JobListingCreate


def create_job_listing(
    db: Session,
    job_listing_create: JobListingCreate,
) -> JobListing:
    job_listing = JobListing(
        title=job_listing_create.title,
        company=job_listing_create.company,
        location=job_listing_create.location,
        source=job_listing_create.source,
        url=job_listing_create.url,
        raw_description=job_listing_create.raw_description,
    )

    db.add(job_listing)
    db.commit()
    db.refresh(job_listing)

    return job_listing


def list_job_listings(db: Session) -> list[JobListing]:
    statement = select(JobListing).order_by(JobListing.created_at.desc())
    return list(db.scalars(statement).all())


def get_job_listing_by_id(
    db: Session,
    job_listing_id: str,
) -> JobListing | None:
    return db.get(JobListing, job_listing_id)
