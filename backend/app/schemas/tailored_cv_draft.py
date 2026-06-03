from pydantic import BaseModel


class TailoredCvDraftResponse(BaseModel):
    cv_angle: str
    target_headline: str
    professional_summary: str
    skills_to_emphasise: list[str]
    experience_themes: list[str]
    ats_keywords: list[str]
    risk_notes: list[str]
    draft_text: str
