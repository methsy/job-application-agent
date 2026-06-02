from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    job_listing_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("job_listings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    responsibilities: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    seniority: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    domain: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    employment_type: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    work_arrangement: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    salary_range: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    application_deadline: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    hard_requirements: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    nice_to_have: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    keywords_for_ats: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

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

    job_listing = relationship("JobListing")
