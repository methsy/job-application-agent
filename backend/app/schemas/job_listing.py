from datetime import datetime

from pydantic import BaseModel, Field


class JobListingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    location: str = Field(default="", max_length=255)
    source: str = Field(default="manual", max_length=100)
    url: str = Field(default="", max_length=1000)
    raw_description: str = Field(min_length=1)


class JobListingRead(BaseModel):
    id: str
    title: str
    company: str
    location: str
    source: str
    url: str
    raw_description: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
