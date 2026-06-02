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
