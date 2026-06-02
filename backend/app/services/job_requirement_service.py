from sqlalchemy.orm import Session

from app.models.job_requirement import JobRequirement
from app.schemas.job_requirements import JobRequirementsExtracted


def get_job_requirement_by_job_listing_id(
    db: Session,
    job_listing_id: str,
) -> JobRequirement | None:
    return (
        db.query(JobRequirement)
        .filter(JobRequirement.job_listing_id == job_listing_id)
        .one_or_none()
    )


def upsert_job_requirement(
    db: Session,
    job_listing_id: str,
    extracted_requirements: JobRequirementsExtracted,
) -> JobRequirement:
    job_requirement = get_job_requirement_by_job_listing_id(
        db=db,
        job_listing_id=job_listing_id,
    )

    requirement_data = extracted_requirements.model_dump()

    if job_requirement is None:
        job_requirement = JobRequirement(
            job_listing_id=job_listing_id,
            **requirement_data,
        )
        db.add(job_requirement)
    else:
        for key, value in requirement_data.items():
            setattr(job_requirement, key, value)

    db.commit()
    db.refresh(job_requirement)

    return job_requirement
