
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import LandCoverRequest
from services.landcover_service import classify_landcover


router = APIRouter(
    prefix="/landcover",
    tags=["Land Cover"],
)


@router.post("/classify")
def classify(
    request: LandCoverRequest,
):
    """
    Classify land cover using Sentinel-2 imagery
    and spectral indices.
    """

    try:
        return classify_landcover(
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
            f"[Land Cover Router] "
            f"Classification error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Land-cover classification failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
