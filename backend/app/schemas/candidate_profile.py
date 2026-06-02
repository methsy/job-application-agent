from datetime import datetime

from pydantic import BaseModel, Field


class ExperienceSummary(BaseModel):
    company: str = ""
    role: str = ""
    summary: str = ""


class CandidateProfileExtracted(BaseModel):
    target_roles: list[str] = Field(default_factory=list)
    core_skills: list[str] = Field(default_factory=list)
    secondary_skills: list[str] = Field(default_factory=list)
    seniority: str = ""
    domains: list[str] = Field(default_factory=list)
    experience_summary: list[ExperienceSummary] = Field(default_factory=list)
    location_preferences: list[str] = Field(default_factory=list)
    work_arrangement_preferences: list[str] = Field(default_factory=list)


class CandidateProfileRead(CandidateProfileExtracted):
    id: str
    cv_profile_id: str
    extraction_notes: str = ""
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
