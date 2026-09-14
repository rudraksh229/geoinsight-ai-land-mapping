import logging
import math
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
    Convert the single XGBoost prediction into
    dashboard land-cover area values.

    Since the current model predicts one class for
    the analyzed area, the complete mapped area is
    assigned to the predicted class.
    """

    class_name = str(
        prediction.get("class_name")
        or prediction.get("label")
        or "Unknown"
    ).strip().lower()

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


def create_circle_geojson(
    latitude: float,
    longitude: float,
    radius: float,
    points: int = 64,
):
    """
    Create a GeoJSON polygon representing the
    analyzed circular area.

    radius is in metres.
    """

    earth_radius = 6378137.0

    coordinates = []

    lat_rad = math.radians(latitude)

    for i in range(points + 1):

        angle = (
            2.0
            * math.pi
            * i
            / points
        )

        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)

        new_lat = (
            latitude
            + (
                dy
                / earth_radius
            )
            * (
                180.0
                / math.pi
            )
        )

        longitude_scale = (
            earth_radius
            * math.cos(lat_rad)
        )

        if longitude_scale == 0:
            new_lng = longitude
        else:
            new_lng = (
                longitude
                + (
                    dx
                    / longitude_scale
                )
                * (
                    180.0
                    / math.pi
                )
            )

        coordinates.append(
            [
                new_lng,
                new_lat,
            ]
        )

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "landClass": "Analyzed Area",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        coordinates
                    ],
                },
            }
        ],
    }


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
    Run GeoInsight AI land analysis.

    Flow:

        Frontend
            ↓
        /mapping/analyze
            ↓
        Google Earth Engine
            ↓
        Sentinel-2 features
            ↓
        XGBoost
            ↓
        Land-cover calculation
            ↓
        Database
            ↓
        Frontend
    """

    start_time = time.time()

    user_id = get_user_id(
        current_user
    )

    latitude = float(
        request_data.lat
    )

    longitude = float(
        request_data.lng
    )

    radius = float(
        request_data.radius
        if request_data.radius is not None
        else 500
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not (
        -90
        <= latitude
        <= 90
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid latitude.",
        )

    if not (
        -180
        <= longitude
        <= 180
    ):
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

        # ====================================================
        # 1. RUN GEE + XGBOOST ANALYSIS
        # ====================================================

        result = AnalysisService.analyze(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        prediction = result.get(
            "prediction",
            {},
        )

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

        if not prediction:
            raise RuntimeError(
                "AI prediction was not returned."
            )

        # ====================================================
        # 2. AREA
        # ====================================================

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

        # ====================================================
        # 3. CONFIDENCE
        # ====================================================

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

        # Make sure confidence is 0-100.
        if 0 <= confidence <= 1:
            confidence = confidence * 100

        confidence = max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        )

        # ====================================================
        # 4. LAND COVER
        # ====================================================

        land_cover = (
            calculate_land_cover_from_prediction(
                prediction=prediction,
                total_area=mapped_area,
            )
        )

        # ====================================================
        # 5. CREATE MAP GEOJSON
        # ====================================================

        map_data = create_circle_geojson(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        # Add useful information to map feature.
        predicted_class = (
            prediction.get(
                "class_name",
                prediction.get(
                    "label",
                    "Unknown",
                ),
            )
        )

        if map_data.get("features"):

            map_data["features"][0][
                "properties"
            ].update(
                {
                    "className": predicted_class,
                    "confidence": round(
                        confidence,
                        2,
                    ),
                    "area": mapped_area,
                }
            )

        # ====================================================
        # 6. SAVE DATABASE RECORD
        # ====================================================

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

            vegetation=land_cover[
                "vegetation"
            ],

            agriculture=land_cover[
                "agriculture"
            ],

            water=land_cover[
                "water"
            ],

            builtup=land_cover[
                "builtup"
            ],

            barren=land_cover[
                "barren"
            ],

            confidence=confidence,

            status="Completed",
        )

        db.add(
            new_analysis
        )

        db.commit()

        db.refresh(
            new_analysis
        )

        # ====================================================
        # 7. REPORT ID
        # ====================================================

        report_id = (
            f"REP-{new_analysis.id}"
        )

        elapsed_time = round(
            time.time()
            - start_time,
            2,
        )

        logger.info(
            "Land analysis completed successfully. "
            "user_id=%s analysis_id=%s class=%s confidence=%s",
            user_id,
            new_analysis.id,
            predicted_class,
            confidence,
        )

        # ====================================================
        # 8. FRONTEND RESPONSE
        # ====================================================

        return {
            "success": True,

            "reportId": report_id,

            # ------------------------------------------------
            # AI PREDICTION
            # ------------------------------------------------

            "prediction": {
                "class_id": prediction.get(
                    "class_id"
                ),

                "label": predicted_class,

                "class_name": predicted_class,

                "confidence": round(
                    confidence / 100,
                    4,
                ),
            },

            # ------------------------------------------------
            # LOCATION
            # ------------------------------------------------

            "location": {
                "state": request_data.state,
                "district": request_data.district,
                "village": request_data.village,
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
            },

            # ------------------------------------------------
            # STATISTICS
            # ------------------------------------------------

            "stats": {
                "totalArea": total_area,

                "mappedArea": mapped_area,

                "confidence": round(
                    confidence,
                    2,
                ),

                "predictionTime": (
                    f"{elapsed_time}s"
                ),
            },

            # ------------------------------------------------
            # RAW GEE DATA
            # ------------------------------------------------

            "statistics": statistics,

            "features": features,

            # ------------------------------------------------
            # MAP DATA
            # ------------------------------------------------

            "mapData": map_data,

            # ------------------------------------------------
            # LAND COVER
            # ------------------------------------------------

            "landCover": {
                "vegetation": round(
                    land_cover[
                        "vegetation"
                    ],
                    2,
                ),

                "agriculture": round(
                    land_cover[
                        "agriculture"
                    ],
                    2,
                ),

                "builtup": round(
                    land_cover[
                        "builtup"
                    ],
                    2,
                ),

                "barren": round(
                    land_cover[
                        "barren"
                    ],
                    2,
                ),

                "water": round(
                    land_cover[
                        "water"
                    ],
                    2,
                ),
            },

            # ------------------------------------------------
            # MESSAGE
            # ------------------------------------------------

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
