from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.cv_profile import CVProfileCreate, CVProfileRead
from app.services.cv_profile_service import (
    create_cv_profile,
    get_cv_profile_by_id,
    list_cv_profiles,
)
from app.services.cv_text_extraction_service import (
    EmptyExtractedTextError,
    UnsupportedFileTypeError,
    extract_text_from_upload,
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


@router.post(
    "/upload",
    response_model=CVProfileRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_cv_profile_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        extracted_text = await extract_text_from_upload(file)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except EmptyExtractedTextError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    cv_profile_create = CVProfileCreate(
        filename=file.filename or "uploaded_cv",
        raw_text=extracted_text,
    )

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
