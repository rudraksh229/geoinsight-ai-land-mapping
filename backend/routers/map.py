
from fastapi import (
    APIRouter,
    HTTPException,
)

from schemas import MapTileRequest
from services.map_service import get_ndvi_tiles


router = APIRouter(
    prefix="/map",
    tags=["Map Tiles"],
)


@router.post("/ndvi")
def ndvi(
    request: MapTileRequest,
):
    """
    Generate an NDVI map tile URL using
    Sentinel-2 imagery from Google Earth Engine.
    """

    try:
        return get_ndvi_tiles(
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
            f"[Map Router] "
            f"NDVI tile generation error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate NDVI map tiles. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
