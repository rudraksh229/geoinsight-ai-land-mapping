
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import ReverseGeocodeRequest
from services.geocode_service import reverse_geocode


router = APIRouter(
    prefix="/geocode",
    tags=["Reverse Geocoding"],
)


@router.post("/reverse")
def reverse(
    request: ReverseGeocodeRequest,
):
    """
    Convert latitude and longitude into
    a human-readable location.
    """

    try:
        return reverse_geocode(
            latitude=request.latitude,
            longitude=request.longitude,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[Geocode Router] "
            f"Reverse geocoding error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Reverse geocoding failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
