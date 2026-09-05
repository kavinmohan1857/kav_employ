import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services import job_service

router = APIRouter()
SessionDependency = Annotated[Session, Depends(get_db)]


def _response(job: object) -> JobResponse:
    return JobResponse.model_validate(job)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreate, session: SessionDependency) -> JobResponse:
    return _response(job_service.create_job(session, job_data))


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, session: SessionDependency) -> JobResponse:
    job = job_service.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _response(job)
