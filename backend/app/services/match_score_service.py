from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.models.job_requirement import JobRequirement
from app.models.match_score import MatchScore
from app.schemas.match_score import MatchScoreCalculated


def create_match_score(
    db: Session,
    candidate_profile: CandidateProfile,
    job_requirement: JobRequirement,
    calculated_score: MatchScoreCalculated,
) -> MatchScore:
    match_score = MatchScore(
        candidate_profile_id=candidate_profile.id,
        job_requirement_id=job_requirement.id,
        **calculated_score.model_dump(),
    )

    db.add(match_score)
    db.commit()
    db.refresh(match_score)

    return match_score


def list_match_scores(db: Session) -> list[MatchScore]:
    statement = select(MatchScore).order_by(MatchScore.created_at.desc())
    return list(db.scalars(statement).all())


def get_match_score_by_id(
    db: Session,
    match_score_id: str,
) -> MatchScore | None:
    return db.get(MatchScore, match_score_id)
