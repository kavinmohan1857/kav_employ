import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.application import Application


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint(
            "entry_level_score BETWEEN 0 AND 100",
            name="ck_jobs_entry_level_score_range",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_jobs_salary_range",
        ),
        CheckConstraint(
            "minimum_years_experience IS NULL OR maximum_years_experience IS NULL "
            "OR minimum_years_experience <= maximum_years_experience",
            name="ck_jobs_experience_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    raw_title: Mapped[str] = mapped_column(String(300), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    raw_company: Mapped[str] = mapped_column(String(300), nullable=False)
    normalized_company: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    raw_location: Mapped[str] = mapped_column(String(300), nullable=False)
    normalized_location: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    workplace_type: Mapped[str | None] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    source_external_id: Mapped[str | None] = mapped_column(String(300))
    source_url: Mapped[str | None] = mapped_column(Text)
    apply_url: Mapped[str | None] = mapped_column(Text)
    date_posted: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    employment_type: Mapped[str | None] = mapped_column(String(30))
    minimum_years_experience: Mapped[float | None] = mapped_column(Numeric(4, 1))
    maximum_years_experience: Mapped[float | None] = mapped_column(Numeric(4, 1))
    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)
    salary_currency: Mapped[str | None] = mapped_column(String(3))
    entry_level_score: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_level_reasons: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    classifier_version: Mapped[str] = mapped_column(String(30), nullable=False)
    duplicate_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    application: Mapped["Application | None"] = relationship(
        back_populates="job", cascade="all, delete-orphan", passive_deletes=True
    )
