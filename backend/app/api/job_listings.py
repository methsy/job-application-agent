from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.job_requirement_extraction_agent import (
    extract_job_requirements_from_listing,
)
from app.core.database import get_db
from app.schemas.job_listing import JobListingCreate, JobListingRead
from app.schemas.job_requirements import JobRequirementRead
from app.services.job_listing_service import (
    create_job_listing,
    get_job_listing_by_id,
    list_job_listings,
)
from app.services.job_requirement_service import (
    get_job_requirement_by_job_listing_id,
    upsert_job_requirement,
)

router = APIRouter(
    prefix="/job-listings",
    tags=["job-listings"],
)


@router.post(
    "",
    response_model=JobListingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_job_listing_endpoint(
    job_listing_create: JobListingCreate,
    db: Session = Depends(get_db),
):
    return create_job_listing(db, job_listing_create)


@router.get(
    "",
    response_model=list[JobListingRead],
)
def list_job_listings_endpoint(
    db: Session = Depends(get_db),
):
    return list_job_listings(db)


@router.post(
    "/{job_listing_id}/extract-requirements",
    response_model=JobRequirementRead,
)
def extract_requirements_from_job_listing_endpoint(
    job_listing_id: str,
    db: Session = Depends(get_db),
):
    job_listing = get_job_listing_by_id(db, job_listing_id)

    if job_listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job listing not found",
        )

    extracted_requirements = extract_job_requirements_from_listing(
        title=job_listing.title,
        company=job_listing.company,
        location=job_listing.location,
        raw_description=job_listing.raw_description,
    )

    return upsert_job_requirement(
        db=db,
        job_listing_id=job_listing_id,
        extracted_requirements=extracted_requirements,
    )


@router.get(
    "/{job_listing_id}/requirements",
    response_model=JobRequirementRead,
)
def get_requirements_for_job_listing_endpoint(
    job_listing_id: str,
    db: Session = Depends(get_db),
):
    job_listing = get_job_listing_by_id(db, job_listing_id)

    if job_listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job listing not found",
        )

    job_requirement = get_job_requirement_by_job_listing_id(
        db=db,
        job_listing_id=job_listing_id,
    )

    if job_requirement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirements not found for this listing",
        )

    return job_requirement


@router.get(
    "/{job_listing_id}",
    response_model=JobListingRead,
)
def get_job_listing_endpoint(
    job_listing_id: str,
    db: Session = Depends(get_db),
):
    job_listing = get_job_listing_by_id(db, job_listing_id)

    if job_listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job listing not found",
        )

    return job_listing
