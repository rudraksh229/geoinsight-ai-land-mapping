
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import BuiltupRequest
from services.builtup_service import builtup_analysis


router = APIRouter(
    prefix="/builtup",
    tags=["Built-up Detection"],
)


@router.post("/detect")
def builtup_detection(
    request: BuiltupRequest,
):
    """
    Detect built-up land using Sentinel-2
    NDBI, NDVI and NDWI analysis.
    """

    try:
        return builtup_analysis(
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
            f"[Built-up Router] "
            f"Built-up analysis error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Built-up land analysis failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
