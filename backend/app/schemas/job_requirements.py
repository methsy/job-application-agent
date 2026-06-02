from pydantic import BaseModel, Field


class JobRequirementsExtracted(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    seniority: str = ""
    domain: str = ""
    employment_type: str = ""
    work_arrangement: str = ""
    location: str = ""
    salary_range: str = ""
    application_deadline: str = ""
    hard_requirements: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    keywords_for_ats: list[str] = Field(default_factory=list)
