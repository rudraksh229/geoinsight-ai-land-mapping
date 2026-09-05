from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import RecommendationRequest
from services.recommendation_service import generate_recommendation


router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation"],
)


@router.post("/")
def recommendation(
    request: RecommendationRequest,
):
    """
    Generate a land-use recommendation based on
    land-cover percentages and NDVI.
    """

    try:
        return generate_recommendation(
            request
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[Recommendation Router] "
            f"Recommendation error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Land-use recommendation failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
        