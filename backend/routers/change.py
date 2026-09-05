from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import ChangeRequest
from services.change_service import detect_change


router = APIRouter(
    prefix="/change",
    tags=["Change Detection"],
)


@router.post("/detect")
def change(
    request: ChangeRequest,
):
    """
    Detect vegetation change between two selected dates
    using Sentinel-2 NDVI.
    """

    try:
        return detect_change(
            latitude=request.latitude,
            longitude=request.longitude,
            radius=request.radius,
            start_date=request.start_date,
            end_date=request.end_date,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[Change Router] Change detection error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Vegetation change detection failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
