from pydantic import BaseModel


class ApplicationAdviceRead(BaseModel):
    decision: str
    best_cv_angle: str
    keywords_to_add: list[str]
    risk_notes: list[str]
    cover_letter_angle: str
    next_action: str
