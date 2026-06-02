from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.job_listing import JobListingCreate, JobListingRead
from app.services.job_listing_service import (
    create_job_listing,
    get_job_listing_by_id,
    list_job_listings,
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
