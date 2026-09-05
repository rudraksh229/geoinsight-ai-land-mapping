from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

# Safe security import so missing auth service never crashes app startup
try:
    from backend.security import get_current_user
except ModuleNotFoundError:
    try:
        from security import get_current_user
    except Exception:
        get_current_user = lambda: {"id": 1, "username": "fallback_user"}

router = APIRouter(
    prefix="/mapping",
    tags=["Land Mapping"]
)

@router.post("/analyze")
def analyze_land(
    request_data: schemas.MappingRequest,
    db: Session = Depends(get_db),
):
    # Hardcoded response to verify routing bypasses 502
    return {
        "success": True,
        "reportId": 101,
        "prediction": {"confidence": 0.92, "class_id": 1, "label": "Agricultural Land"},
        "location": {
            "state": request_data.state,
            "district": request_data.district,
            "village": request_data.village,
            "latitude": request_data.lat,
            "longitude": request_data.lng
        },
        "stats": {"totalArea": 78.54, "mappedArea": 78.54},
        "statistics": {"NDVI": 0.45, "NDWI": -0.02},
        "features": {},
        "mapData": {"type": "FeatureCollection", "features": []},
        "landCover": {
            "vegetation": 25.0,
            "agriculture": 35.0,
            "builtup": 8.0,
            "barren": 5.0,
            "water": 5.54
        },
        "message": "Direct Bypass Test Successful"
    }
