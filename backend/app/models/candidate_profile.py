from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    cv_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cv_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    target_roles: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    core_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    secondary_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    seniority: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    domains: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    experience_summary: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    location_preferences: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    work_arrangement_preferences: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    extraction_notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    cv_profile = relationship("CVProfile")
    