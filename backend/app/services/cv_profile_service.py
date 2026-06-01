from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cv_profile import CVProfile
from app.schemas.cv_profile import CVProfileCreate


def create_cv_profile(
    db: Session,
    cv_profile_create: CVProfileCreate,
) -> CVProfile:
    cv_profile = CVProfile(
        filename=cv_profile_create.filename,
        raw_text=cv_profile_create.raw_text,
    )

    db.add(cv_profile)
    db.commit()
    db.refresh(cv_profile)

    return cv_profile


def list_cv_profiles(db: Session) -> list[CVProfile]:
    statement = select(CVProfile).order_by(CVProfile.created_at.desc())
    return list(db.scalars(statement).all())


def get_cv_profile_by_id(
    db: Session,
    cv_profile_id: str,
) -> CVProfile | None:
    return db.get(CVProfile, cv_profile_id)
