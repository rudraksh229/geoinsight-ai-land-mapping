import logging
import math
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from schemas import MappingRequest
from database import get_db
from security import get_current_user

from services.analysis_service import AnalysisService
from ai.feature_extractor import extract_feature_grid
from ai.predictor import predict_land_grid


router = APIRouter(
    prefix="/mapping",
    tags=["Land Mapping"],
)

logger = logging.getLogger(__name__)


# =========================================================
# HELPERS
# =========================================================

def get_user_id(current_user):
    """
    Safely get user ID from the authenticated user.
    """

    if current_user is None:
        return None

    if hasattr(current_user, "id"):
        return current_user.id

    if isinstance(current_user, dict):
        return current_user.get("id")

    return None


# =========================================================
# LAND COVER COLOR
# =========================================================

def get_land_cover_color(class_id=None, class_name=None):
    """
    Return map color according to predicted land-cover class.
    Handles both encoded class IDs and decoded class labels.
    """

    # --------------------------------------------------------
    # First try actual class_id
    # --------------------------------------------------------

    if class_id is not None:
        try:
            class_id = int(class_id)

            # Actual land-cover classes
            if class_id in [10, 20, 30, 90]:
                return "#22c55e"

            if class_id == 40:
                return "#eab308"

            if class_id == 50:
                return "#ef4444"

            if class_id == 60:
                return "#a16207"

            if class_id == 80:
                return "#3b82f6"

        except (TypeError, ValueError):
            pass

    # --------------------------------------------------------
    # IMPORTANT:
    # class_name may contain decoded numeric label
    # Example: encoded 4 -> class_name "50"
    # --------------------------------------------------------

    if class_name is not None:
        try:
            decoded_class_id = int(class_name)

            if decoded_class_id in [10, 20, 30, 90]:
                return "#22c55e"

            if decoded_class_id == 40:
                return "#eab308"

            if decoded_class_id == 50:
                return "#ef4444"

            if decoded_class_id == 60:
                return "#a16207"

            if decoded_class_id == 80:
                return "#3b82f6"

        except (TypeError, ValueError):
            pass

        # ----------------------------------------------------
        # Text labels
        # ----------------------------------------------------

        name = str(class_name).lower().strip()

        if (
            "vegetation" in name
            or "forest" in name
            or "grass" in name
            or "shrub" in name
        ):
            return "#22c55e"

        if (
            "agriculture" in name
            or "crop" in name
            or "cropland" in name
        ):
            return "#eab308"

        if (
            "built" in name
            or "urban" in name
            or "settlement" in name
        ):
            return "#ef4444"

        if (
            "barren" in name
            or "bare" in name
            or "fallow" in name
            or "dry" in name
            or "wasteland" in name
        ):
            return "#a16207"

        if (
            "water" in name
            or "river" in name
            or "lake" in name
            or "pond" in name
        ):
            return "#3b82f6"

    return "#94a3b8"


# =========================================================
# LAND COVER CATEGORY
# =========================================================

def get_land_cover_category(class_id=None, class_name=None):
    """
    Convert predicted class into dashboard category.
    Handles both encoded class IDs and decoded class labels.
    """

    # --------------------------------------------------------
    # First try actual class_id
    # --------------------------------------------------------

    if class_id is not None:
        try:
            class_id = int(class_id)

            if class_id in [10, 20, 30, 90]:
                return "vegetation"

            if class_id == 40:
                return "agriculture"

            if class_id == 50:
                return "builtup"

            if class_id == 60:
                return "barren"

            if class_id == 80:
                return "water"

        except (TypeError, ValueError):
            pass

    # --------------------------------------------------------
    # IMPORTANT:
    # class_name may contain decoded numeric label
    # Example: encoded 4 -> class_name "50"
    # --------------------------------------------------------

    if class_name is not None:
        try:
            decoded_class_id = int(class_name)

            if decoded_class_id in [10, 20, 30, 90]:
                return "vegetation"

            if decoded_class_id == 40:
                return "agriculture"

            if decoded_class_id == 50:
                return "builtup"

            if decoded_class_id == 60:
                return "barren"

            if decoded_class_id == 80:
                return "water"

        except (TypeError, ValueError):
            pass

        # ----------------------------------------------------
        # Text labels
        # ----------------------------------------------------

        name = str(class_name).lower().strip()

        if "vegetation" in name or "forest" in name:
            return "vegetation"

        if "agriculture" in name or "crop" in name:
            return "agriculture"

        if "built" in name or "urban" in name:
            return "builtup"

        if "barren" in name:
            return "barren"

        if "water" in name:
            return "water"

    return "unknown"


# =========================================================
# CREATE GRID GEOJSON
# =========================================================

def create_grid_geojson(predictions):
    """
    Convert grid predictions into GeoJSON FeatureCollection.
    """

    features = []

    for prediction in predictions:

        geometry = prediction.get("geometry")

        if not geometry:
            continue

        class_id = prediction.get("class_id")
        class_name = prediction.get("class_name")

        label = prediction.get(
            "label",
            class_name,
        )

        category = get_land_cover_category(
            class_id=class_id,
            class_name=class_name,
        )

        color = get_land_cover_color(
            class_id=class_id,
            class_name=class_name,
        )

        try:
            area_ha = float(
                prediction.get(
                    "area_ha",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            area_ha = 0.0

        feature = {
            "type": "Feature",

            "geometry": geometry,

            "properties": {
                "gridId": prediction.get(
                    "grid_id"
                ),

                "classId": class_id,

                "className": class_name,

                "label": label,

                "landClass": category,

                "confidence": prediction.get(
                    "confidence",
                    0.0,
                ),

                "area": round(
                    area_ha,
                    4,
                ),

                "areaHa": round(
                    area_ha,
                    4,
                ),

                "color": color,
            },
        }

        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }


# =========================================================
# CALCULATE LAND COVER AREA
# =========================================================

def calculate_grid_land_cover(predictions):
    """
    Calculate total area for every predicted land-cover category.
    """

    land_cover = {
        "vegetation": 0.0,
        "agriculture": 0.0,
        "barren": 0.0,
        "water": 0.0,
        "builtup": 0.0,
    }

    for prediction in predictions:

        category = get_land_cover_category(
            class_id=prediction.get(
                "class_id"
            ),
            class_name=prediction.get(
                "class_name"
            ),
        )

        if category not in land_cover:
            continue

        try:
            area_ha = float(
                prediction.get(
                    "area_ha",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            area_ha = 0.0

        land_cover[category] += area_ha

    return {
        key: round(value, 2)
        for key, value in land_cover.items()
    }


# =========================================================
# FALLBACK CIRCLE GEOJSON
# =========================================================

def create_circle_geojson(
    latitude,
    longitude,
    radius,
):
    """
    Fallback geometry when grid mapping is unavailable.
    """

    return {
        "type": "FeatureCollection",

        "features": [
            {
                "type": "Feature",

                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        longitude,
                        latitude,
                    ],
                },

                "properties": {
                    "radius": radius,
                    "color": "#94a3b8",
                },
            }
        ],
    }


# =========================================================
# ANALYZE LAND
# =========================================================

@router.post("/analyze")
def analyze_land(
    request_data: MappingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Analyze selected geographical area.

    Flow:

    1. Validate request
    2. Extract regional features
    3. Generate grid
    4. Predict every grid cell
    5. Generate multi-color GeoJSON
    6. Calculate land-cover areas
    7. Save analysis in PostgreSQL
    8. Return complete mapping result
    """

    start_time = time.time()

    try:

        # =================================================
        # VALIDATION
        # =================================================

        # IMPORTANT:
        # MappingRequest uses lat/lng, not latitude/longitude.

        latitude = float(
            request_data.lat
        )

        longitude = float(
            request_data.lng
        )

        radius = float(
            request_data.radius
        )

        if latitude < -90 or latitude > 90:
            raise HTTPException(
                status_code=400,
                detail="Invalid latitude.",
            )

        if longitude < -180 or longitude > 180:
            raise HTTPException(
                status_code=400,
                detail="Invalid longitude.",
            )

        if radius <= 0:
            raise HTTPException(
                status_code=400,
                detail="Radius must be greater than zero.",
            )

        if radius > 10000:
            raise HTTPException(
                status_code=400,
                detail="Radius cannot exceed 10000 meters.",
            )

        logger.info(
            "Starting land analysis: lat=%s lon=%s radius=%s",
            latitude,
            longitude,
            radius,
        )

        # =================================================
        # STEP 1 — REGIONAL ANALYSIS
        # =================================================

        analysis_service = AnalysisService()

        regional_result = analysis_service.analyze(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        prediction = regional_result.get(
            "prediction",
            {},
        )

        statistics = regional_result.get(
            "statistics",
            {},
        )

        regional_features = regional_result.get(
            "features",
            {},
        )

        stats = regional_result.get(
            "stats",
            {},
        )

        total_area = regional_result.get(
            "total_area",
            0.0,
        )

        try:
            total_area = float(
                total_area
            )
        except (TypeError, ValueError):
            total_area = (
                math.pi
                * (radius ** 2)
                / 10000.0
            )

        # =================================================
        # STEP 2 — CREATE FEATURE GRID
        # =================================================

        logger.info(
            "Creating land-cover grid..."
        )

        grid_features = extract_feature_grid(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            grid_size=100,
        )

        logger.info(
            "Grid feature extraction completed: %s cells",
            len(grid_features),
        )

        # =================================================
        # STEP 3 — PREDICT EVERY GRID CELL
        # =================================================

        grid_predictions = predict_land_grid(
            grid_features
        )

        logger.info(
            "Grid prediction completed: %s cells",
            len(grid_predictions),
        )

        # =================================================
        # STEP 4 — CREATE MULTI-COLOR GEOJSON
        # =================================================

        map_data = create_grid_geojson(
            grid_predictions
        )

        # =================================================
        # STEP 5 — CALCULATE LAND COVER
        # =================================================

        land_cover = calculate_grid_land_cover(
            grid_predictions
        )

        mapped_area = sum(
            land_cover.values()
        )

        mapped_area = round(
            mapped_area,
            2,
        )

        # =================================================
        # FALLBACK AREA
        # =================================================

        if mapped_area <= 0:

            try:
                mapped_area = float(
                    regional_result.get(
                        "mapped_area",
                        0.0,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                mapped_area = 0.0

        # =================================================
        # CONFIDENCE
        # =================================================

        confidence = prediction.get(
            "confidence",
            0.0,
        )

        try:
            confidence = float(
                confidence
            )

        except (
            TypeError,
            ValueError,
        ):
            confidence = 0.0

        # Store confidence as percentage
        # in the database.

        db_confidence = confidence

        if db_confidence <= 1:
            db_confidence *= 100

        db_confidence = round(
            db_confidence,
            2,
        )

        # =================================================
        # USER
        # =================================================

        user_id = get_user_id(
            current_user
        )

        # =================================================
        # STEP 6 — SAVE ANALYSIS
        # =================================================

        analysis = models.Analysis(

            user_id=user_id,

            village=getattr(
                request_data,
                "village",
                "Unknown",
            ),

            district=getattr(
                request_data,
                "district",
                "Unknown",
            ),

            state=getattr(
                request_data,
                "state",
                "Unknown",
            ),

            latitude=latitude,

            longitude=longitude,

            radius=radius,

            date=datetime.utcnow(),

            total_area=round(
                total_area,
                2,
            ),

            mapped_area=mapped_area,

            vegetation=land_cover[
                "vegetation"
            ],

            agriculture=land_cover[
                "agriculture"
            ],

            barren=land_cover[
                "barren"
            ],

            water=land_cover[
                "water"
            ],

            builtup=land_cover[
                "builtup"
            ],

            confidence=db_confidence,

            status="Completed",
        )

        db.add(analysis)

        db.commit()

        db.refresh(analysis)

        # =================================================
        # PROCESSING TIME
        # =================================================

        processing_time = round(
            time.time()
            - start_time,
            2,
        )

        # =================================================
        # RESPONSE
        # =================================================

        return {

            "success": True,

            "prediction": prediction,

            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
            },

            "stats": stats,

            "statistics": statistics,

            "features": regional_features,

            "mapData": map_data,

            "landCover": {

                "vegetation": land_cover[
                    "vegetation"
                ],

                "agriculture": land_cover[
                    "agriculture"
                ],

                "barren": land_cover[
                    "barren"
                ],

                "water": land_cover[
                    "water"
                ],

                "builtup": land_cover[
                    "builtup"
                ],
            },

            "grid": {

                "totalCells": len(
                    grid_features
                ),

                "predictedCells": len(
                    grid_predictions
                ),

                "gridSize": 100,
            },

            "analysisId": analysis.id,

            "message": (
                "AI classification generated "
                "successfully."
            ),

            "processingTime": processing_time,

            "created_at": (
                analysis.created_at
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Land mapping analysis failed."
        )

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Land mapping analysis failed: "
                f"{str(exc)}"
            ),
        ) from exc
