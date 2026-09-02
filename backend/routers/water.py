from fastapi import APIRouter
from pydantic import BaseModel

from services.water_service import detect_water

router = APIRouter(
    prefix="/water",
    tags=["Water Detection"]
)


class WaterRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float


@router.post("/detect")
def water_detection(data: WaterRequest):
    return detect_water(
        data.latitude,
        data.longitude,
        data.radius,
    )
