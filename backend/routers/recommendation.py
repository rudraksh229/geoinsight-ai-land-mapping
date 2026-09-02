from fastapi import APIRouter

from schemas import RecommendationRequest
from services.recommendation_service import generate_recommendation

router = APIRouter(
    prefix="/recommendation",
    tags=["AI Recommendation"]
)


@router.post("/")
def recommendation(request: RecommendationRequest):
    return generate_recommendation(request)
