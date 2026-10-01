from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseOperationError
from app.models.application import Application
from app.models.job import Job
from app.schemas.application import ApplicationStatus
from app.schemas.dashboard import DashboardSummaryResponse

SUBMITTED_STATUSES = (
    ApplicationStatus.APPLIED.value,
    ApplicationStatus.INTERVIEW.value,
    ApplicationStatus.REJECTED.value,
    ApplicationStatus.OFFER.value,
    ApplicationStatus.WITHDRAWN.value,
)


def get_dashboard_summary(
    session: Session, *, now: datetime | None = None
) -> DashboardSummaryResponse:
    current_time = now or datetime.now(UTC)
    week_start = (current_time - timedelta(days=current_time.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    try:
        job_totals = session.execute(
            select(
                func.count(Job.id),
                func.count(Job.id).filter(Job.entry_level_score >= 70),
                func.count(Job.id).filter(Job.first_seen_at >= week_start),
            )
        ).one()
        applications_submitted = session.scalar(
            select(func.count(Application.id)).where(Application.status.in_(SUBMITTED_STATUSES))
        )
    except SQLAlchemyError as error:
        session.rollback()
        raise DatabaseOperationError("Dashboard statistics could not be loaded") from error

    return DashboardSummaryResponse(
        total_jobs=job_totals[0],
        likely_entry_level_jobs=job_totals[1],
        jobs_added_this_week=job_totals[2],
        applications_submitted=applications_submitted or 0,
    )
