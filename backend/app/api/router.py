from fastapi import APIRouter

from app.api.routes import applications, dashboard, jobs

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/jobs", tags=["applications"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
