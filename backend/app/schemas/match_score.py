from datetime import datetime

from pydantic import BaseModel, Field


class MatchScoreCreate(BaseModel):
    candidate_profile_id: str = Field(min_length=1)
    job_requirement_id: str = Field(min_length=1)


class MatchScoreBreakdown(BaseModel):
    technical_skill_score: int
    responsibility_score: int
    seniority_score: int
    domain_score: int
    location_score: int
    constraints_score: int
    career_strategy_score: int


class MatchScoreCalculated(BaseModel):
    total_score: int
    technical_skill_score: int
    responsibility_score: int
    seniority_score: int
    domain_score: int
    location_score: int
    constraints_score: int
    career_strategy_score: int
    recommendation: str
    matched_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)
    matched_responsibilities: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    reasoning_summary: str = ""


class MatchScoreRead(MatchScoreCalculated):
    id: str
    candidate_profile_id: str
    job_requirement_id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
