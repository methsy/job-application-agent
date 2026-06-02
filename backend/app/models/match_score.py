from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MatchScore(Base):
    __tablename__ = "match_scores"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    candidate_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_requirement_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("job_requirements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    total_score: Mapped[int] = mapped_column(Integer, nullable=False)

    technical_skill_score: Mapped[int] = mapped_column(Integer, nullable=False)
    responsibility_score: Mapped[int] = mapped_column(Integer, nullable=False)
    seniority_score: Mapped[int] = mapped_column(Integer, nullable=False)
    domain_score: Mapped[int] = mapped_column(Integer, nullable=False)
    location_score: Mapped[int] = mapped_column(Integer, nullable=False)
    constraints_score: Mapped[int] = mapped_column(Integer, nullable=False)
    career_strategy_score: Mapped[int] = mapped_column(Integer, nullable=False)

    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)

    matched_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_required_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    matched_preferred_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    matched_responsibilities: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    gaps: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    reasoning_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    candidate_profile = relationship("CandidateProfile")
    job_requirement = relationship("JobRequirement")
