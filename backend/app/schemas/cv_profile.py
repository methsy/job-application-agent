from datetime import datetime

from pydantic import BaseModel, Field


class CVProfileCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    raw_text: str = Field(min_length=1)


class CVProfileRead(BaseModel):
    id: str
    filename: str
    raw_text: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
