from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import TimeSeriesRequest
from services.time_series_service import vegetation_timeseries


router = APIRouter(
    prefix="/timeseries",
    tags=["Time Series"],
)


@router.post("/vegetation")
def vegetation(
    request: TimeSeriesRequest,
):
    """
    Generate vegetation NDVI time-series data
    for the selected location and date range.
    """

    try:
        return vegetation_timeseries(
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
            f"[Time Series Router] Analysis error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Vegetation time-series analysis failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
