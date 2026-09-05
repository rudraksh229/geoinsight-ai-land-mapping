
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import WaterRequest
from services.water_service import water_analysis


router = APIRouter(
    prefix="/water",
    tags=["Water Detection"],
)


@router.post("/detect")
def water_detection(
    request: WaterRequest,
):
    """
    Detect water bodies using Sentinel-2
    NDWI-based analysis.
    """

    try:
        return water_analysis(
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
            f"[Water Router] "
            f"Water analysis error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Water-body analysis failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
