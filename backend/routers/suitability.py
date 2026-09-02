from fastapi import APIRouter

from schemas import SuitabilityRequest
from services.suitability_service import analyze_suitability

router = APIRouter(
    prefix="/suitability",
    tags=["AI Suitability"]
)


@router.post("/score")
def score(request: SuitabilityRequest):

    return analyze_suitability(
        request.latitude,
        request.longitude,
        request.radius,
    )
