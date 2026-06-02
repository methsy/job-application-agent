from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.schemas.match_score import MatchScoreCreate, MatchScoreRead
from app.services.match_score_service import (
    create_match_score,
    get_match_score_by_id,
    list_match_scores,
)
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
