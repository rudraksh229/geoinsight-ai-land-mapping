from fastapi import APIRouter

from schemas import ReverseGeocodeRequest
from services.geocode_service import reverse_geocode

router = APIRouter(
    prefix="/geocode",
    tags=["Reverse Geocoding"]
)


@router.post("/reverse")
def reverse(request: ReverseGeocodeRequest):

    return reverse_geocode(
        request.latitude,
        request.longitude
    )
