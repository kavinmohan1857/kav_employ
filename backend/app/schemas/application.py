import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ApplicationStatus(StrEnum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"
    WITHDRAWN = "withdrawn"


class ApplicationUpsert(BaseModel):
    status: ApplicationStatus
    date_applied: datetime | None = None
    notes: str | None = None
    referral: bool = False
    interview_stage: str | None = Field(default=None, max_length=100)

    @field_validator("notes", "interview_stage")
    @classmethod
    def reject_blank_optional_strings(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def validate_interview_stage(self):
        if self.interview_stage is not None and self.status != ApplicationStatus.INTERVIEW:
            raise ValueError("interview_stage is only valid when status is interview")
        return self


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    status: ApplicationStatus
    date_applied: datetime | None
    notes: str | None
    referral: bool
    interview_stage: str | None
    created_at: datetime
    updated_at: datetime
