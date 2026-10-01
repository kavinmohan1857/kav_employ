import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.application import ApplicationResponse, ApplicationUpsert
from app.services import application_service, job_service

router = APIRouter()
SessionDependency = Annotated[Session, Depends(get_db)]


def _require_job(session: Session, job_id: uuid.UUID) -> None:
    if job_service.get_job(session, job_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")


@router.put("/{job_id}/application", response_model=ApplicationResponse)
def upsert_application(
    job_id: uuid.UUID,
    application_data: ApplicationUpsert,
    response: Response,
    session: SessionDependency,
) -> ApplicationResponse:
    _require_job(session, job_id)
    application, created = application_service.upsert_application(session, job_id, application_data)
    if created:
        response.status_code = status.HTTP_201_CREATED
    return ApplicationResponse.model_validate(application)


@router.get("/{job_id}/application", response_model=ApplicationResponse)
def get_application(job_id: uuid.UUID, session: SessionDependency) -> ApplicationResponse:
    _require_job(session, job_id)
    application = application_service.get_application(session, job_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application tracking not found"
        )
    return ApplicationResponse.model_validate(application)


@router.delete("/{job_id}/application", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(job_id: uuid.UUID, session: SessionDependency) -> Response:
    _require_job(session, job_id)
    application = application_service.get_application(session, job_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application tracking not found"
        )
    application_service.delete_application(session, application)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
