
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import BarrenRequest
from services.barren_service import barren_land_analysis


router = APIRouter(
    prefix="/barren",
    tags=["Barren Land"],
)


@router.post("/detect")
def detect(
    request: BarrenRequest,
):
    """
    Detect barren land using Sentinel-2 imagery
    and spectral indices.
    """

    try:
        return barren_land_analysis(
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
            f"[Barren Router] "
            f"Barren-land analysis error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Barren-land analysis failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
