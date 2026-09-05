
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import CompareRequest
from services.compare_service import compare_locations


router = APIRouter(
    prefix="/compare",
    tags=["Compare Locations"],
)


@router.post("/")
def compare(
    request: CompareRequest,
):
    """
    Compare land-cover statistics between
    two selected locations.
    """

    try:
        return compare_locations(
            location1=request.location1,
            location2=request.location2,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[Compare Router] "
            f"Location comparison error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Location comparison failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
