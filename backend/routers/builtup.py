from fastapi import APIRouter
from pydantic import BaseModel

from services.builtup_service import detect_builtup

router = APIRouter(
    prefix="/builtup",
    tags=["Built-up Detection"]
)


class BuiltupRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float


@router.post("/detect")
def builtup_detection(data: BuiltupRequest):
    return detect_builtup(
        data.latitude,
        data.longitude,
        data.radius,
    )
