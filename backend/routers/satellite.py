from fastapi import APIRouter

from schemas import SatelliteRequest
from services.satellite_service import get_satellite_image

router = APIRouter(
    prefix="/satellite",
    tags=["Satellite Image"]
)


@router.post("/image")
def satellite_image(request: SatelliteRequest):

    return get_satellite_image(
        request.latitude,
        request.longitude,
        request.radius
    )
