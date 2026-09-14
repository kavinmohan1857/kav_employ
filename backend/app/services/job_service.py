import uuid
from dataclasses import asdict
from typing import Any

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseOperationError, InvalidJobUpdateError
from app.db.transactions import commit_or_raise
from app.intelligence.duplicate_fingerprint import build_duplicate_fingerprint
from app.intelligence.entry_level_classifier import classify_entry_level
from app.intelligence.normalization import normalize_company, normalize_location
from app.intelligence.title_normalizer import normalize_title
from app.models.job import Job
from app.schemas.job import EntryLevelSuitability, JobCreate, JobSortField, JobUpdate, SortOrder

WRITABLE_FIELDS = tuple(JobCreate.model_fields)


def _serialize_input(job_data: JobCreate) -> dict[str, Any]:
    values = job_data.model_dump(mode="python")
    for url_field in ("source_url", "apply_url"):
        if values[url_field] is not None:
            values[url_field] = str(values[url_field])
    if values["salary_currency"] is not None:
        values["salary_currency"] = values["salary_currency"].upper()
    return values


def _derived_values(job_data: JobCreate) -> dict[str, Any]:
    normalized_title = normalize_title(job_data.raw_title)
    normalized_company = normalize_company(job_data.raw_company)
    normalized_location = normalize_location(job_data.raw_location)
    classification = classify_entry_level(
        raw_title=job_data.raw_title,
        description=job_data.description,
        minimum_years_experience=job_data.minimum_years_experience,
        maximum_years_experience=job_data.maximum_years_experience,
    )
    return {
        "normalized_title": normalized_title,
        "normalized_company": normalized_company,
        "normalized_location": normalized_location,
        "entry_level_score": classification.score,
        "entry_level_reasons": [asdict(reason) for reason in classification.reasons],
        "classifier_version": classification.version,
        "duplicate_fingerprint": build_duplicate_fingerprint(
            normalized_company=normalized_company,
            normalized_title=normalized_title,
            normalized_location=normalized_location,
        ),
    }


def create_job(session: Session, job_data: JobCreate) -> Job:
    job = Job(**_serialize_input(job_data), **_derived_values(job_data))
    session.add(job)
    commit_or_raise(session)
    session.refresh(job)
    return job


def get_job(session: Session, job_id: uuid.UUID) -> Job | None:
    try:
        return session.get(Job, job_id)
    except SQLAlchemyError as error:
        session.rollback()
        raise DatabaseOperationError("The database query could not be completed") from error


def list_jobs(
    session: Session,
    *,
    company: str | None,
    title: str | None,
    location: str | None,
    suitability: EntryLevelSuitability | None,
    sort_by: JobSortField,
    sort_order: SortOrder,
    limit: int,
    offset: int,
) -> tuple[list[Job], int]:
    filters = []
    if company:
        filters.append(Job.normalized_company.contains(normalize_company(company)))
    if title:
        filters.append(func.lower(Job.normalized_title).contains(normalize_title(title).lower()))
    if location:
        filters.append(Job.normalized_location.contains(normalize_location(location)))
    if suitability == EntryLevelSuitability.LIKELY:
        filters.append(Job.entry_level_score >= 70)
    elif suitability == EntryLevelSuitability.UNCERTAIN:
        filters.extend((Job.entry_level_score >= 40, Job.entry_level_score < 70))
    elif suitability == EntryLevelSuitability.UNLIKELY:
        filters.append(Job.entry_level_score < 40)

    try:
        total = session.scalar(select(func.count()).select_from(Job).where(*filters)) or 0
        sort_column = getattr(Job, sort_by.value)
        ordering = sort_column.asc() if sort_order == SortOrder.ASC else sort_column.desc()
        statement = (
            select(Job).where(*filters).order_by(ordering, Job.id.asc()).limit(limit).offset(offset)
        )
        return list(session.scalars(statement)), total
    except SQLAlchemyError as error:
        session.rollback()
        raise DatabaseOperationError("The database query could not be completed") from error


def update_job(session: Session, job: Job, update_data: JobUpdate) -> Job:
    current = {field: getattr(job, field) for field in WRITABLE_FIELDS}
    current.update(update_data.model_dump(exclude_unset=True, mode="python"))
    try:
        validated = JobCreate.model_validate(current)
    except ValidationError as error:
        raise InvalidJobUpdateError("The update creates an invalid job") from error

    for field, value in _serialize_input(validated).items():
        setattr(job, field, value)
    for field, value in _derived_values(validated).items():
        setattr(job, field, value)

    commit_or_raise(session)
    session.refresh(job)
    return job


def delete_job(session: Session, job: Job) -> None:
    session.delete(job)
    commit_or_raise(session)
