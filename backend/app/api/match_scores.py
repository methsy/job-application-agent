from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.schemas.match_score import (
    MatchScoreCreate,
    MatchScoreRead,
    MatchScoreFromCvAndJobCreate,
)
from app.services.match_score_service import (
    create_match_score,
    get_match_score_by_id,
    list_match_scores,
)

from app.services import cv_profile_service
from app.services import job_listing_service
from app.services import candidate_profile_service
from app.services import job_requirement_service

from app.services.match_scoring_service import calculate_match_score

router = APIRouter(
    prefix="/match-scores",
    tags=["match-scores"],
)


@router.post(
    "",
    response_model=MatchScoreRead,
    status_code=status.HTTP_201_CREATED,
)
def create_match_score_endpoint(
    match_score_create: MatchScoreCreate,
    db: Session = Depends(get_db),
):
    candidate_profile = db.get(
        CandidateProfile,
        match_score_create.candidate_profile_id,
    )

    if candidate_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found",
        )

    job_requirement = db.get(
        JobRequirement,
        match_score_create.job_requirement_id,
    )

    if job_requirement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement not found",
        )

    calculated_score = calculate_match_score(
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    return create_match_score(
        db=db,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
        calculated_score=calculated_score,
    )


@router.get(
    "",
    response_model=list[MatchScoreRead],
)
def list_match_scores_endpoint(
    db: Session = Depends(get_db),
):
    return list_match_scores(db)


@router.post(
    "/from-cv-and-job",
    response_model=MatchScoreRead,
    status_code=status.HTTP_201_CREATED,
)
def create_match_score_from_cv_and_job_endpoint(
    match_score_create: MatchScoreFromCvAndJobCreate,
    db: Session = Depends(get_db),
):
    cv_profile = cv_profile_service.get_cv_profile_by_id(
        db=db,
        cv_profile_id=match_score_create.cv_profile_id,
    )

    if cv_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV profile not found",
        )

    job_listing = job_listing_service.get_job_listing_by_id(
        db=db,
        job_listing_id=match_score_create.job_listing_id,
    )

    if job_listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job listing not found",
        )

    candidate_profile = candidate_profile_service.get_candidate_profile_by_cv_profile_id(
        db=db,
        cv_profile_id=match_score_create.cv_profile_id,
    )

    job_requirement = job_requirement_service.get_job_requirement_by_job_listing_id(
        db=db,
        job_listing_id=match_score_create.job_listing_id,
    )

    missing_items = []

    if candidate_profile is None:
        missing_items.append("candidate_profile")

    if job_requirement is None:
        missing_items.append("job_requirement")

    if missing_items and not match_score_create.auto_extract_missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Required extracted data is missing.",
                "missing": missing_items,
                "hint": "Extract the missing records first or retry with auto_extract_missing=true.",
            },
        )

    if missing_items and match_score_create.auto_extract_missing:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "message": "auto_extract_missing=true is not implemented yet.",
                "missing": missing_items,
            },
        )

    calculated_score = calculate_match_score(
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    return create_match_score(
        db=db,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
        calculated_score=calculated_score,
    )


@router.get(
    "/{match_score_id}",
    response_model=MatchScoreRead,
)
def get_match_score_endpoint(
    match_score_id: str,
    db: Session = Depends(get_db),
):
    match_score = get_match_score_by_id(
        db=db,
        match_score_id=match_score_id,
    )

    if match_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match score not found",
        )

    return match_score
