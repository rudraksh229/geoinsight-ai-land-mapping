from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import SuitabilityRequest
from services.suitability_service import analyze_suitability


router = APIRouter(
    prefix="/suitability",
    tags=["Land Suitability"],
)


@router.post("/score")
def score(
    request: SuitabilityRequest,
):
    """
    Analyze land suitability for the selected location.
    """

    try:
        return analyze_suitability(
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
            f"[Suitability Router] Analysis error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Land suitability analysis failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
