from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas

from database import get_db
from services.analysis_service import AnalysisService
from services.landcover_service import classify_landcover
from security import get_current_user


router = APIRouter(
    prefix="/mapping",
    tags=["Land Mapping"]
)


@router.post("/analyze")
def analyze_land(
    request: schemas.MappingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # ==========================================
    # AI ANALYSIS
    # ==========================================

    analysis_result = AnalysisService.analyze(
        latitude=request.lat,
        longitude=request.lng,
        radius=500
    )

    # ==========================================
    # SPATIAL LAND COVER MAP
    # ==========================================

    landcover_result = classify_landcover(
        latitude=request.lat,
        longitude=request.lng,
        radius=500
    )

    # ==========================================
    # DATABASE ANALYSIS
    # ==========================================

    analysis = models.Analysis(
        user_id=current_user.id,

        village=request.village,
        district=request.district,
        state=request.state,

        date=datetime.strptime(
            request.date,
            "%Y-%m-%d"
        ),

        total_area=analysis_result["stats"]["totalArea"],
        mapped_area=analysis_result["stats"]["mappedArea"],

        vegetation=landcover_result["vegetation_ha"],
        agriculture=landcover_result["agriculture_ha"],
        water=landcover_result["water_ha"],
        builtup=landcover_result["builtup_ha"],
        barren=landcover_result["barren_ha"],

        confidence=analysis_result["prediction"]["confidence"],

        status=str(
            analysis_result["prediction"]["class_id"]
        )
    )

    # ==========================================
    # SAVE
    # ==========================================

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # ==========================================
    # RESPONSE
    # ==========================================

    return {
        "success": True,

        "reportId": analysis.id,

        "prediction": analysis_result["prediction"],

        "location": {
            "state": request.state,
            "district": request.district,
            "village": request.village,
            "latitude": request.lat,
            "longitude": request.lng
        },

        "stats": analysis_result["stats"],

        "statistics": analysis_result["statistics"],

        "features": analysis_result["features"],

        # ======================================
        # ACTUAL GEOJSON MAP
        # ======================================

        "mapData": landcover_result["mapData"],

        "landCover": {
            "vegetation": landcover_result["vegetation_ha"],
            "agriculture": landcover_result["agriculture_ha"],
            "builtup": landcover_result["builtup_ha"],
            "barren": landcover_result["barren_ha"],
            "water": landcover_result["water_ha"]
        },

        "message": (
            "Prediction and spatial classification "
            "completed successfully."
        )
    }
    