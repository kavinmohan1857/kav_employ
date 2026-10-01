from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter()
SessionDependency = Annotated[Session, Depends(get_db)]


@router.get("/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(session: SessionDependency) -> DashboardSummaryResponse:
    return get_dashboard_summary(session)
