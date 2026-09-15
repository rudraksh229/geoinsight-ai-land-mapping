import logging
import math
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from schemas import MappingRequest
from database import get_db
from auth import get_current_user

from services.analysis_service import AnalysisService
from ai.feature_extractor import extract_feature_grid
from ai.predictor import predict_land_grid


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/mapping",
    tags=["Mapping"]
)


# ============================================================
# USER ID HELPER
# ============================================================

def get_user_id(current_user):

    if isinstance(
        current_user,
        dict
    ):

        return (
            current_user.get("id")
            or current_user.get("user_id")
        )

    return (
        getattr(
            current_user,
            "id",
            None
        )
        or getattr(
            current_user,
            "user_id",
            None
        )
    )


# ============================================================
# LAND-COVER COLOR
# ============================================================

def get_land_cover_color(class_name):

    if class_name is None:
        return "#6b7280"

    class_name = str(
        class_name
    ).strip().lower()

    # WorldCover numeric classes
    if class_name in ["10", "20", "30", "90"]:
        return "#22c55e"

    if class_name == "40":
        return "#eab308"

    if class_name == "50":
        return "#ef4444"

    if class_name == "60":
        return "#a16207"

    if class_name == "80":
        return "#3b82f6"

    # Text labels
    if "vegetation" in class_name:
        return "#22c55e"

    if "agriculture" in class_name:
        return "#eab308"

    if "built" in class_name or "urban" in class_name:
        return "#ef4444"

    if "barren" in class_name:
        return "#a16207"

    if "water" in class_name:
        return "#3b82f6"

    return "#6b7280"


# ============================================================
# LAND-COVER CATEGORY
# ============================================================

def get_land_cover_category(class_name):

    if class_name is None:
        return None

    value = str(
        class_name
    ).strip().lower()

    # WorldCover codes
    if value in ["10", "20", "30", "90"]:
        return "vegetation"

    if value == "40":
        return "agriculture"

    if value == "50":
        return "builtup"

    if value == "60":
        return "barren"

    if value == "80":
        return "water"

    # Text labels
    if "vegetation" in value:
        return "vegetation"

    if "agriculture" in value:
        return "agriculture"

    if "built" in value or "urban" in value:
        return "builtup"

    if "barren" in value:
        return "barren"

    if "water" in value:
        return "water"

    return None


# ============================================================
# CREATE GRID GEOJSON
# ============================================================

def create_grid_geojson(
    grid_predictions
):

    features = []

    for prediction in grid_predictions:

        geometry = prediction.get(
            "geometry"
        )

        if not geometry:
            continue

        class_name = prediction.get(
            "class_name"
        )

        category = get_land_cover_category(
            class_name
        )

        color = get_land_cover_color(
            class_name
        )

        area_ha = prediction.get(
            "area_ha",
            0.0
        )

        confidence = prediction.get(
            "confidence",
            0.0
        )

        features.append(
            {
                "type": "Feature",

                "properties":
                {
                    "gridId": prediction.get(
                        "grid_id"
                    ),

                    "classId": prediction.get(
                        "class_id"
                    ),

                    "className": class_name,

                    "label": prediction.get(
                        "label",
                        class_name
                    ),

                    "landClass": (
                        category
                        if category
                        else class_name
                    ),

                    "confidence": confidence,

                    "area": area_ha,

                    "color": color,
                },

                "geometry": geometry,
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features
    }


# ============================================================
# CALCULATE LAND-COVER TOTALS
# ============================================================

def calculate_grid_land_cover(
    grid_predictions
):

    land_cover = {
        "vegetation": 0.0,
        "agriculture": 0.0,
        "barren": 0.0,
        "water": 0.0,
        "builtup": 0.0,
    }

    for prediction in grid_predictions:

        class_name = prediction.get(
            "class_name"
        )

        category = get_land_cover_category(
            class_name
        )

        if category is None:
            continue

        try:

            area_ha = float(
                prediction.get(
                    "area_ha",
                    0.0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            area_ha = 0.0

        land_cover[
            category
        ] += area_ha

    # Round values for API response
    for key in land_cover:

        land_cover[key] = round(
            land_cover[key],
            2
        )

    return land_cover


# ============================================================
# CREATE FALLBACK CIRCLE GEOJSON
# ============================================================

def create_circle_geojson(
    latitude,
    longitude,
    radius,
    points=64
):

    coordinates = []

    earth_radius = 6378137.0

    lat_rad = math.radians(
        latitude
    )

    for i in range(
        points + 1
    ):

        angle = (
            2
            * math.pi
            * i
            / points
        )

        dx = (
            radius
            * math.cos(angle)
        )

        dy = (
            radius
            * math.sin(angle)
        )

        delta_lat = (
            dy
            / earth_radius
        )

        delta_lng = (
            dx
            / (
                earth_radius
                * math.cos(lat_rad)
            )
        )

        new_lat = (
            latitude
            + math.degrees(
                delta_lat
            )
        )

        new_lng = (
            longitude
            + math.degrees(
                delta_lng
            )
        )

        coordinates.append(
            [
                new_lng,
                new_lat
            ]
        )

    return {
        "type": "FeatureCollection",

        "features":
        [
            {
                "type": "Feature",

                "properties":
                {
                    "landClass":
                        "Analyzed Area"
                },

                "geometry":
                {
                    "type": "Polygon",

                    "coordinates":
                    [
                        coordinates
                    ]
                }
            }
        ]
    }


# ============================================================
# ANALYZE LAND
# ============================================================

@router.post(
    "/analyze"
)
def analyze_land(
    request_data: schemas.MappingRequest,
    db: Session = Depends(
        get_db
    ),
    current_user=Depends(
        get_current_user
    )
):

    start_time = time.time()

    try:

        # ----------------------------------------------------
        # Validate coordinates
        # ----------------------------------------------------

        latitude = float(
            request_data.lat
        )

        longitude = float(
            request_data.lng
        )

        radius = float(
            getattr(
                request_data,
                "radius",
                500
            )
        )

        if not (
            -90
            <= latitude
            <= 90
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid latitude."
            )

        if not (
            -180
            <= longitude
            <= 180
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid longitude."
            )

        if radius <= 0:

            raise HTTPException(
                status_code=400,
                detail="Radius must be greater than zero."
            )

        # ----------------------------------------------------
        # Existing regional analysis
        # ----------------------------------------------------

        logger.info(
            "Starting regional land analysis: lat=%s lng=%s radius=%s",
            latitude,
            longitude,
            radius
        )

        analysis_result = (
            AnalysisService.analyze(
                latitude,
                longitude,
                radius
            )
        )

        prediction = (
            analysis_result.get(
                "prediction",
                {}
            )
        )

        statistics = (
            analysis_result.get(
                "statistics",
                {}
            )
        )

        features = (
            analysis_result.get(
                "features",
                {}
            )
        )

        stats = (
            analysis_result.get(
                "stats",
                {}
            )
        )

        # ----------------------------------------------------
        # Total area
        # ----------------------------------------------------

        total_area = float(
            stats.get(
                "totalArea",
                (
                    math.pi
                    * radius
                    * radius
                    / 10000
                )
            )
        )

        # ----------------------------------------------------
        # GRID FEATURE EXTRACTION
        # ----------------------------------------------------

        logger.info(
            "Extracting land-cover feature grid..."
        )

        grid_features = (
            extract_feature_grid(
                latitude,
                longitude,
                radius,
                grid_size=100
            )
        )

        logger.info(
            "Grid feature extraction completed. "
            "Cells received: %s",
            len(grid_features)
        )

        if not grid_features:

            raise RuntimeError(
                "No grid features were generated."
            )

        # ----------------------------------------------------
        # GRID XGBOOST PREDICTION
        # ----------------------------------------------------

        logger.info(
            "Running XGBoost prediction for grid cells..."
        )

        grid_predictions = (
            predict_land_grid(
                grid_features
            )
        )

        logger.info(
            "Grid prediction completed. "
            "Predictions: %s",
            len(grid_predictions)
        )

        if not grid_predictions:

            raise RuntimeError(
                "No grid predictions were generated."
            )

        # ----------------------------------------------------
        # CREATE MULTI-COLOR MAP
        # ----------------------------------------------------

        map_data = create_grid_geojson(
            grid_predictions
        )

        # ----------------------------------------------------
        # LAND-COVER TOTALS
        # ----------------------------------------------------

        land_cover = (
            calculate_grid_land_cover(
                grid_predictions
            )
        )

        mapped_area = round(
            sum(
                land_cover.values()
            ),
            2
        )

        # If no recognizable classes were
        # produced, use the regional mapped area.
        if mapped_area <= 0:

            mapped_area = float(
                stats.get(
                    "mappedArea",
                    total_area
                )
            )

        # ----------------------------------------------------
        # CONFIDENCE
        # ----------------------------------------------------

        confidence = float(
            prediction.get(
                "confidence",
                0
            )
        )

        # Normalize if model returned
        # a value between 0 and 1.
        if (
            0
            <= confidence
            <= 1
        ):

            confidence *= 100

        confidence = round(
            confidence,
            2
        )

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        user_id = get_user_id(
            current_user
        )

        # ----------------------------------------------------
        # SAVE ANALYSIS
        # ----------------------------------------------------

        analysis = models.Analysis(

            user_id=user_id,

            village=getattr(
                request_data,
                "village",
                None
            ),

            district=getattr(
                request_data,
                "district",
                None
            ),

            state=getattr(
                request_data,
                "state",
                None
            ),

            date=getattr(
                request_data,
                "date",
                None
            ),

            total_area=round(
                total_area,
                2
            ),

            mapped_area=round(
                mapped_area,
                2
            ),

            confidence=confidence,

            status="Completed",

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
        )

        db.add(
            analysis
        )

        db.commit()

        db.refresh(
            analysis
        )

        # ----------------------------------------------------
        # PROCESSING TIME
        # ----------------------------------------------------

        processing_time = round(
            time.time()
            - start_time,
            2
        )

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return {

            "success": True,

            "prediction":
            {
                "class_id":
                    prediction.get(
                        "class_id"
                    ),

                "label":
                    prediction.get(
                        "label"
                    ),

                "class_name":
                    prediction.get(
                        "class_name"
                    ),

                "confidence":
                    round(
                        confidence / 100,
                        4
                    ),
            },

            "location":
            {
                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "radius":
                    radius,
            },

            "stats":
            {
                "totalArea":
                    round(
                        total_area,
                        2
                    ),

                "mappedArea":
                    round(
                        mapped_area,
                        2
                    ),

                "processingTime":
                    processing_time,
            },

            "statistics":
                statistics,

            "features":
                features,

            "mapData":
                map_data,

            "landCover":
                land_cover,

            "grid":
            {
                "totalCells":
                    len(grid_features),

                "predictedCells":
                    len(grid_predictions),
            },

            "message":
                "AI classification generated successfully.",

            "created_at":
                datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Land analysis failed."
        )

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Land analysis failed. "
                f"Reason: {str(exc)}"
            )
        )
