
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import SatelliteRequest
from services.satellite_service import get_satellite_image


router = APIRouter(
    prefix="/satellite",
    tags=["Satellite Image"],
)


@router.post("/image")
def satellite_image(
    request: SatelliteRequest,
):
    """
    Generate a Sentinel-2 RGB satellite image
    for the selected location and radius.
    """

    try:
        return get_satellite_image(
            latitude=request.latitude,
            longitude=request.longitude,
            radius=request.radius,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[Satellite Router] "
            f"Satellite image generation error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Satellite image generation failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc