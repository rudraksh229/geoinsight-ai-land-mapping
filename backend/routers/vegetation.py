from fastapi import APIRouter

from schemas import VegetationRequest
from services.vegetation_service import vegetation_health


router = APIRouter(
    prefix="/vegetation",
    tags=["Vegetation Health"],
)


@router.post("/health")
def health(
    request: VegetationRequest,
):
    """
    Analyze vegetation health using Sentinel-2 NDVI
    for the requested date range.
    """

    return vegetation_health(
        latitude=request.latitude,
        longitude=request.longitude,
        radius=request.radius,
        start_date=request.start_date,
        end_date=request.end_date,
    )
