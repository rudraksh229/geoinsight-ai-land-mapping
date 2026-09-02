from fastapi import APIRouter

from schemas import CompareRequest
from services.compare_service import compare_locations

router = APIRouter(
    prefix="/compare",
    tags=["Compare Locations"]
)


@router.post("/")
def compare(request: CompareRequest):

    return compare_locations(
        request.location1,
        request.location2,
    )