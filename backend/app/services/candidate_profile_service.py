from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.schemas.candidate_profile import CandidateProfileExtracted


def get_candidate_profile_by_cv_profile_id(
    db: Session,
    cv_profile_id: str,
) -> CandidateProfile | None:
    return (
        db.query(CandidateProfile)
        .filter(CandidateProfile.cv_profile_id == cv_profile_id)
        .one_or_none()
    )


def upsert_candidate_profile(
    db: Session,
    cv_profile_id: str,
    extracted_profile: CandidateProfileExtracted,
) -> CandidateProfile:
    candidate_profile = get_candidate_profile_by_cv_profile_id(
        db=db,
        cv_profile_id=cv_profile_id,
    )

    profile_data = extracted_profile.model_dump()

    if candidate_profile is None:
        candidate_profile = CandidateProfile(
            cv_profile_id=cv_profile_id,
            **profile_data,
        )
        db.add(candidate_profile)
    else:
        for key, value in profile_data.items():
            setattr(candidate_profile, key, value)

    db.commit()
    db.refresh(candidate_profile)

    return candidate_profile
