from fastapi import APIRouter
from pydantic import BaseModel

from services.vegetation_service import vegetation_health

router = APIRouter(
    prefix="/vegetation",
    tags=["Vegetation Health"],
)


class VegetationRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float


@router.post("/health")
def health(request: VegetationRequest):
    return vegetation_health(
        request.latitude,
        request.longitude,
        request.radius,
    )
    