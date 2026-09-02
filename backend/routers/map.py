from fastapi import APIRouter

from schemas import MapTileRequest
from services.map_service import get_ndvi_tiles

router = APIRouter(
    prefix="/map",
    tags=["Map Tiles"]
)


@router.post("/ndvi")
def ndvi(request: MapTileRequest):

    return get_ndvi_tiles(
        request.latitude,
        request.longitude,
        request.radius
    )
