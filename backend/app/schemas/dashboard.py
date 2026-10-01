from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_jobs: int
    likely_entry_level_jobs: int
    jobs_added_this_week: int
    applications_submitted: int
