from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.intelligence.personal_fit import CandidateProfile, PersonalFit, analyze_personal_fit

router = APIRouter()


class AnalysisRequest(BaseModel):
    description: str = Field(min_length=1, max_length=100000)
    profile: CandidateProfile = Field(default_factory=CandidateProfile)


@router.post("/personal-fit", response_model=PersonalFit)
def personal_fit(request: AnalysisRequest) -> PersonalFit:
    return analyze_personal_fit(request.description, request.profile)
