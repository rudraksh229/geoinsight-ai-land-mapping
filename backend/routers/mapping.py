from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas

from database import get_db
# Absolute path fallback imports
try:
    from backend.services.analysis_service import AnalysisService
    from backend.services.landcover_service import classify_landcover
    from backend.security import get_current_user
except ModuleNotFoundError:
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
    try:
        # ==========================================
        # 1. AI ANALYSIS
        # ==========================================
        analysis_result = AnalysisService.analyze(
            latitude=request.lat,
            longitude=request.lng,
            radius=500
        )

        # ==========================================
        # 2. SPATIAL LAND COVER MAP
        # ==========================================
        landcover_result = classify_landcover(
            latitude=request.lat,
            longitude=request.lng,
            radius=500
        )

        # Parse Date Safely
        try:
            parsed_date = datetime.strptime(request.date, "%Y-%m-%d")
        except ValueError:
            parsed_date = datetime.utcnow()

        # ==========================================
        # 3. DATABASE ANALYSIS
        # ==========================================
        analysis = models.Analysis(
            user_id=current_user.id,
            village=request.village,
            district=request.district,
            state=request.state,
            date=parsed_date,
            total_area=analysis_result.get("stats", {}).get("totalArea", 0),
            mapped_area=analysis_result.get("stats", {}).get("mappedArea", 0),
            vegetation=landcover_result.get("vegetation_ha", 0),
            agriculture=landcover_result.get("agriculture_ha", 0),
            water=landcover_result.get("water_ha", 0),
            builtup=landcover_result.get("builtup_ha", 0),
            barren=landcover_result.get("barren_ha", 0),
            confidence=analysis_result.get("prediction", {}).get("confidence", 0.0),
            status=str(analysis_result.get("prediction", {}).get("class_id", "0"))
        )

        # ==========================================
        # 4. SAVE TO DATABASE
        # ==========================================
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # ==========================================
        # 5. RESPONSE
        # ==========================================
        return {
            "success": True,
            "reportId": analysis.id,
            "prediction": analysis_result.get("prediction", {}),
            "location": {
                "state": request.state,
                "district": request.district,
                "village": request.village,
                "latitude": request.lat,
                "longitude": request.lng
            },
            "stats": analysis_result.get("stats", {}),
            "statistics": analysis_result.get("statistics", {}),
            "features": analysis_result.get("features", {}),
            "mapData": landcover_result.get("mapData", {}),
            "landCover": {
                "vegetation": landcover_result.get("vegetation_ha", 0),
                "agriculture": landcover_result.get("agriculture_ha", 0),
                "builtup": landcover_result.get("builtup_ha", 0),
                "barren": landcover_result.get("barren_ha", 0),
                "water": landcover_result.get("water_ha", 0)
            },
            "message": "Prediction and spatial classification completed successfully."
        }

    except Exception as e:
        print(f"Error in /mapping/analyze endpoint: {str(e)}")
        # Database Rollback if transaction failed
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Land Analysis Error: {str(e)}"
        )