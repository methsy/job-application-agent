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
from app.agents.cv_profile_extraction_agent import extract_candidate_profile_from_cv
from app.agents.job_requirement_extraction_agent import extract_job_requirements_from_listing
from app.services.candidate_profile_service import upsert_candidate_profile
from app.services.job_requirement_service import upsert_job_requirement
from app.schemas.application_advice import ApplicationAdviceRead
from app.services.application_advice_service import get_application_advice_by_match_score_id
from app.schemas.tailored_cv_draft import TailoredCvDraftResponse
from app.services.application_advice_service import generate_application_advice
from app.services.tailored_cv_draft_service import generate_tailored_cv_draft

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
        if candidate_profile is None:
            extracted_profile = extract_candidate_profile_from_cv(
                cv_profile.raw_text
            )

            candidate_profile = upsert_candidate_profile(
                db=db,
                cv_profile_id=match_score_create.cv_profile_id,
                extracted_profile=extracted_profile,
            )

        if job_requirement is None:
            extracted_requirements = extract_job_requirements_from_listing(
                title=job_listing.title,
                company=job_listing.company,
                location=job_listing.location,
                raw_description=job_listing.raw_description,
            )

            job_requirement = upsert_job_requirement(
                db=db,
                job_listing_id=match_score_create.job_listing_id,
                extracted_requirements=extracted_requirements,
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


@router.get("/{match_score_id}/application-advice", response_model=ApplicationAdviceRead)
def get_application_advice(
    match_score_id: str,
    db: Session = Depends(get_db),
):
    advice = get_application_advice_by_match_score_id(
        db=db,
        match_score_id=match_score_id,
    )

    if advice is None:
        raise HTTPException(
            status_code=404,
            detail="Match score or linked records not found",
        )

    return advice


@router.get(
    "/{match_score_id}/tailored-cv-draft",
    response_model=TailoredCvDraftResponse,
)
def get_tailored_cv_draft(match_score_id: str, db: Session = Depends(get_db)):
    match_score = get_match_score_by_id(db=db, match_score_id=match_score_id)

    if match_score is None:
        raise HTTPException(status_code=404, detail="Match score not found")

    candidate_profile = db.get(
        CandidateProfile,
        match_score.candidate_profile_id,
    )

    if candidate_profile is None:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    job_requirement = db.get(
        JobRequirement,
        match_score.job_requirement_id,
    )

    if job_requirement is None:
        raise HTTPException(status_code=404, detail="Job requirement not found")

    application_advice = generate_application_advice(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
    )

    return generate_tailored_cv_draft(
        match_score=match_score,
        candidate_profile=candidate_profile,
        job_requirement=job_requirement,
        application_advice=application_advice,
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
