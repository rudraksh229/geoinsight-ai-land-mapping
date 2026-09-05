import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas

from database import get_db
from security import get_current_user

try:
    from backend.services.analysis_service import AnalysisService
except ModuleNotFoundError:
    from services.analysis_service import AnalysisService


router = APIRouter(
    prefix="/mapping",
    tags=["Land Mapping"],
)

logger = logging.getLogger(__name__)


# ============================================================
# HELPERS
# ============================================================

def get_user_id(current_user) -> int:
    """
    Safely extract the authenticated user's database ID.
    """
    if isinstance(current_user, dict):
        user_id = current_user.get("id")
    else:
        user_id = getattr(current_user, "id", None)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user information is missing.",
        )

    return int(user_id)


def calculate_land_cover_from_prediction(
    prediction: dict,
    total_area: float,
):
    """
    The XGBoost predictor currently predicts one land class
    for the analyzed location.

    Until pixel-level classification is connected, represent
    the predicted class as the mapped land-cover category.
    """

    class_name = str(
        prediction.get("class_name")
        or prediction.get("label")
        or "Unknown"
    ).lower()

    values = {
        "vegetation": 0.0,
        "agriculture": 0.0,
        "barren": 0.0,
        "water": 0.0,
        "builtup": 0.0,
    }

    if "vegetation" in class_name:
        values["vegetation"] = total_area

    elif "agriculture" in class_name:
        values["agriculture"] = total_area

    elif "barren" in class_name:
        values["barren"] = total_area

    elif "water" in class_name:
        values["water"] = total_area

    elif "built" in class_name or "urban" in class_name:
        values["builtup"] = total_area

    return values


# ============================================================
# MAIN LAND MAPPING ENDPOINT
# ============================================================

@router.post("/analyze")
def analyze_land(
    request_data: schemas.MappingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Run the actual GeoInsight AI land-analysis pipeline.

    Flow:

        Frontend
            ↓
        /mapping/analyze
            ↓
        Google Earth Engine
            ↓
        Sentinel-2 features
            ↓
        XGBoost classifier
            ↓
        Database
            ↓
        Frontend response
    """

    start_time = time.time()

    user_id = get_user_id(current_user)

    latitude = float(request_data.lat)
    longitude = float(request_data.lng)

    radius = float(
        request_data.radius
        if request_data.radius is not None
        else 500
    )

    if not (-90 <= latitude <= 90):
        raise HTTPException(
            status_code=400,
            detail="Invalid latitude.",
        )

    if not (-180 <= longitude <= 180):
        raise HTTPException(
            status_code=400,
            detail="Invalid longitude.",
        )

    if radius <= 0:
        raise HTTPException(
            status_code=400,
            detail="Radius must be greater than zero.",
        )

    try:
        # ----------------------------------------------------
        # 1. REAL GEE + XGBOOST ANALYSIS
        # ----------------------------------------------------

        result = AnalysisService.analyze(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        prediction = result.get("prediction", {})

        statistics = result.get(
            "statistics",
            {},
        )

        features = result.get(
            "features",
            {},
        )

        stats = result.get(
            "stats",
            {},
        )

        # ----------------------------------------------------
        # 2. AREA
        # ----------------------------------------------------

        total_area = float(
            stats.get(
                "totalArea",
                0.0,
            )
            or 0.0
        )

        mapped_area = float(
            stats.get(
                "mappedArea",
                total_area,
            )
            or total_area
        )

        # ----------------------------------------------------
        # 3. CONFIDENCE
        # ----------------------------------------------------

        confidence = float(
            prediction.get(
                "confidence",
                stats.get(
                    "confidence",
                    0.0,
                ),
            )
            or 0.0
        )

        # ----------------------------------------------------
        # 4. LAND-COVER RESULT
        # ----------------------------------------------------

        land_cover = calculate_land_cover_from_prediction(
            prediction,
            mapped_area,
        )

        # ----------------------------------------------------
        # 5. SAVE ANALYSIS TO DATABASE
        # ----------------------------------------------------

        new_analysis = models.Analysis(
            user_id=user_id,

            village=request_data.village,
            district=request_data.district,
            state=request_data.state,

            latitude=latitude,
            longitude=longitude,
            radius=radius,

            date=datetime.utcnow(),

            total_area=total_area,
            mapped_area=mapped_area,

            vegetation=land_cover["vegetation"],
            agriculture=land_cover["agriculture"],
            water=land_cover["water"],
            builtup=land_cover["builtup"],
            barren=land_cover["barren"],

            confidence=confidence,

            status="Completed",
        )

        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)

        report_id = f"REP-{new_analysis.id}"

        elapsed_time = round(
            time.time() - start_time,
            2,
        )

        logger.info(
            "Land analysis completed successfully. "
            "user_id=%s analysis_id=%s",
            user_id,
            new_analysis.id,
        )

        # ----------------------------------------------------
        # 6. FRONTEND RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,

            "reportId": report_id,

            "prediction": {
                "class_id": prediction.get(
                    "class_id"
                ),

                "label": prediction.get(
                    "class_name",
                    prediction.get(
                        "label",
                        "Unknown",
                    ),
                ),

                "class_name": prediction.get(
                    "class_name",
                    prediction.get(
                        "label",
                        "Unknown",
                    ),
                ),

                "confidence": round(
                    confidence / 100,
                    4,
                )
                if confidence > 1
                else round(
                    confidence,
                    4,
                ),
            },

            "location": {
                "state": request_data.state,
                "district": request_data.district,
                "village": request_data.village,
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
            },

            "stats": {
                "totalArea": total_area,
                "mappedArea": mapped_area,
                "confidence": confidence,
                "predictionTime": (
                    f"{elapsed_time}s"
                ),
            },

            "statistics": statistics,

            "features": features,

            # Keep existing frontend key.
            "mapData": {
                "type": "FeatureCollection",
                "features": [],
            },

            "landCover": {
                "vegetation": land_cover[
                    "vegetation"
                ],

                "agriculture": land_cover[
                    "agriculture"
                ],

                "builtup": land_cover[
                    "builtup"
                ],

                "barren": land_cover[
                    "barren"
                ],

                "water": land_cover[
                    "water"
                ],
            },

            "message": (
                "Satellite Imagery Analysis "
                "Completed Successfully"
            ),

            "created_at": (
                new_analysis.created_at
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Land mapping analysis failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Land mapping analysis failed. "
                f"Reason: {str(exc)}"
            ),
        )
