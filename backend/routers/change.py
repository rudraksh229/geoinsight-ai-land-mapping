from fastapi import APIRouter

from schemas import ChangeRequest
from services.change_service import detect_change

router = APIRouter(
    prefix="/change",
    tags=["Change Detection"]
)


@router.post("/detect")
def change(request: ChangeRequest):
    return detect_change(
        request.latitude,
        request.longitude,
        request.radius,
        request.start_date,
        request.end_date,
    )
