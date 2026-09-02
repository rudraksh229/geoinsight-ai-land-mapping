from fastapi import APIRouter
from pydantic import BaseModel

from services.barren_service import detect_barren_land


router = APIRouter(
    prefix="/barren",
    tags=["Barren Land"]
)


class BarrenRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int


@router.post("/detect")
def detect(data: BarrenRequest):

    return detect_barren_land(
        data.latitude,
        data.longitude,
        data.radius,
    )
