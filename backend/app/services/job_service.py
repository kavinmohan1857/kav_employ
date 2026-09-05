import uuid
from dataclasses import asdict

from sqlalchemy.orm import Session

from app.intelligence.duplicate_fingerprint import build_duplicate_fingerprint
from app.intelligence.entry_level_classifier import classify_entry_level
from app.intelligence.normalization import normalize_company, normalize_location
from app.intelligence.title_normalizer import normalize_title
from app.models.job import Job
from app.schemas.job import JobCreate


def create_job(session: Session, job_data: JobCreate) -> Job:
    normalized_title = normalize_title(job_data.raw_title)
    normalized_company = normalize_company(job_data.raw_company)
    normalized_location = normalize_location(job_data.raw_location)
    classification = classify_entry_level(
        raw_title=job_data.raw_title,
        description=job_data.description,
        minimum_years_experience=job_data.minimum_years_experience,
        maximum_years_experience=job_data.maximum_years_experience,
    )

    values = job_data.model_dump(mode="python")
    for url_field in ("source_url", "apply_url"):
        if values[url_field] is not None:
            values[url_field] = str(values[url_field])
    if values["salary_currency"] is not None:
        values["salary_currency"] = values["salary_currency"].upper()

    job = Job(
        **values,
        normalized_title=normalized_title,
        normalized_company=normalized_company,
        normalized_location=normalized_location,
        entry_level_score=classification.score,
        entry_level_reasons=[asdict(reason) for reason in classification.reasons],
        classifier_version=classification.version,
        duplicate_fingerprint=build_duplicate_fingerprint(
            normalized_company=normalized_company,
            normalized_title=normalized_title,
            normalized_location=normalized_location,
        ),
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_job(session: Session, job_id: uuid.UUID) -> Job | None:
    return session.get(Job, job_id)
