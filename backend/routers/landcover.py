from fastapi import APIRouter
from pydantic import BaseModel

from services.landcover_service import classify_landcover

router = APIRouter(
    prefix="/landcover",
    tags=["Land Cover"]
)


class LandCoverRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


@router.post("/classify")
def classify(request: LandCoverRequest):
    return classify_landcover(
        request.latitude,
        request.longitude,
        request.radius,
    )
