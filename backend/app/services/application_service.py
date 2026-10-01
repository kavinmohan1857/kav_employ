import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseOperationError
from app.db.transactions import commit_or_raise
from app.models.application import Application
from app.schemas.application import ApplicationStatus, ApplicationUpsert

SUBMITTED_STATUSES = {
    ApplicationStatus.APPLIED,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.REJECTED,
    ApplicationStatus.OFFER,
    ApplicationStatus.WITHDRAWN,
}


def get_application(session: Session, job_id: uuid.UUID) -> Application | None:
    try:
        return session.scalar(select(Application).where(Application.job_id == job_id))
    except SQLAlchemyError as error:
        session.rollback()
        raise DatabaseOperationError("The database query could not be completed") from error


def upsert_application(
    session: Session, job_id: uuid.UUID, data: ApplicationUpsert
) -> tuple[Application, bool]:
    application = get_application(session, job_id)
    created = application is None
    if application is None:
        application = Application(job_id=job_id)
        session.add(application)

    date_applied = data.date_applied or application.date_applied
    if date_applied is None and data.status in SUBMITTED_STATUSES:
        date_applied = datetime.now(UTC)

    application.status = data.status.value
    application.date_applied = date_applied
    application.notes = data.notes
    application.referral = data.referral
    application.interview_stage = data.interview_stage
    commit_or_raise(session)
    session.refresh(application)
    return application, created


def delete_application(session: Session, application: Application) -> None:
    session.delete(application)
    commit_or_raise(session)
