from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.cv_profile import CVProfileCreate, CVProfileRead
from app.services.cv_profile_service import (
    create_cv_profile,
    get_cv_profile_by_id,
    list_cv_profiles,
)

router = APIRouter(
    prefix="/cv-profiles",
    tags=["cv-profiles"],
)


@router.post(
    "",
    response_model=CVProfileRead,
    status_code=status.HTTP_201_CREATED,
)
def create_cv_profile_endpoint(
    cv_profile_create: CVProfileCreate,
    db: Session = Depends(get_db),
):
    return create_cv_profile(db, cv_profile_create)


@router.get(
    "",
    response_model=list[CVProfileRead],
)
def list_cv_profiles_endpoint(
    db: Session = Depends(get_db),
):
    return list_cv_profiles(db)


@router.get(
    "/{cv_profile_id}",
    response_model=CVProfileRead,
)
def get_cv_profile_endpoint(
    cv_profile_id: str,
    db: Session = Depends(get_db),
):
    cv_profile = get_cv_profile_by_id(db, cv_profile_id)

    if cv_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV profile not found",
        )

    return cv_profile
