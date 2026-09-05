import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, model_validator


class WorkplaceType(StrEnum):
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    REMOTE = "remote"
    UNKNOWN = "unknown"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"


class JobCreate(BaseModel):
    raw_title: str = Field(min_length=1, max_length=300)
    raw_company: str = Field(min_length=1, max_length=300)
    raw_location: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1)
    workplace_type: WorkplaceType | None = None
    source: str = Field(default="manual", min_length=1, max_length=100)
    source_external_id: str | None = Field(default=None, max_length=300)
    source_url: HttpUrl | None = None
    apply_url: HttpUrl | None = None
    date_posted: datetime | None = None
    employment_type: EmploymentType | None = None
    minimum_years_experience: float | None = Field(default=None, ge=0, le=99)
    maximum_years_experience: float | None = Field(default=None, ge=0, le=99)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, pattern=r"^[A-Za-z]{3}$")

    @model_validator(mode="after")
    def validate_ranges(self) -> Self:
        if (
            self.minimum_years_experience is not None
            and self.maximum_years_experience is not None
            and self.minimum_years_experience > self.maximum_years_experience
        ):
            raise ValueError("minimum_years_experience cannot exceed maximum_years_experience")
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot exceed salary_max")
        return self


class ClassificationReasonResponse(BaseModel):
    rule: str
    contribution: int
    message: str


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    raw_title: str
    normalized_title: str
    raw_company: str
    normalized_company: str
    raw_location: str
    normalized_location: str
    workplace_type: str | None
    description: str
    source: str
    source_external_id: str | None
    source_url: str | None
    apply_url: str | None
    date_posted: datetime | None
    first_seen_at: datetime
    last_seen_at: datetime
    employment_type: str | None
    minimum_years_experience: float | None
    maximum_years_experience: float | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    entry_level_score: int
    entry_level_reasons: list[dict[str, Any]]
    classifier_version: str
    duplicate_fingerprint: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def entry_level_classification(self) -> str:
        if self.entry_level_score >= 70:
            return "likely"
        if self.entry_level_score >= 40:
            return "uncertain"
        return "unlikely"
