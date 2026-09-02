from fastapi import APIRouter

from schemas import TimeSeriesRequest
from services.timeseries_service import vegetation_timeseries

router = APIRouter(
    prefix="/timeseries",
    tags=["Time Series"]
)


@router.post("/vegetation")
def vegetation(request: TimeSeriesRequest):

    return vegetation_timeseries(
        request.latitude,
        request.longitude,
        request.radius,
        request.start_date,
        request.end_date,
    )
