import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import (
    EntryLevelSuitability,
    JobCreate,
    JobListResponse,
    JobResponse,
    JobSortField,
    JobUpdate,
    SortOrder,
)
from app.services import job_service

router = APIRouter()
SessionDependency = Annotated[Session, Depends(get_db)]


def _response(job: object) -> JobResponse:
    return JobResponse.model_validate(job)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreate, session: SessionDependency) -> JobResponse:
    return _response(job_service.create_job(session, job_data))


@router.get("", response_model=JobListResponse)
def list_jobs(
    session: SessionDependency,
    company: str | None = None,
    title: str | None = None,
    location: str | None = None,
    suitability: EntryLevelSuitability | None = None,
    sort_by: JobSortField = JobSortField.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> JobListResponse:
    jobs, total = job_service.list_jobs(
        session,
        company=company,
        title=title,
        location=location,
        suitability=suitability,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return JobListResponse(
        items=[_response(job) for job in jobs], total=total, limit=limit, offset=offset
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, session: SessionDependency) -> JobResponse:
    job = job_service.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _response(job)


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: uuid.UUID, update_data: JobUpdate, session: SessionDependency
) -> JobResponse:
    job = job_service.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _response(job_service.update_job(session, job, update_data))


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: uuid.UUID, session: SessionDependency) -> Response:
    job = job_service.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    job_service.delete_job(session, job)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
