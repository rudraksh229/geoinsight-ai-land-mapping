import math

import ee

from gee_config import init_gee


# ============================================================
# LAND SUITABILITY ANALYSIS
# ============================================================

def analyze_suitability(
    latitude,
    longitude,
    radius,
):
    """
    Analyze land suitability using Sentinel-2 spectral indices.

    This is a rule-based suitability analysis service.
    The primary AI land classification is handled separately
    by the XGBoost pipeline in /mapping/analyze.
    """

    latitude = float(latitude)
    longitude = float(longitude)
    radius = float(radius)

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not (-90 <= latitude <= 90):
        raise ValueError(
            "Invalid latitude."
        )

    if not (-180 <= longitude <= 180):
        raise ValueError(
            "Invalid longitude."
        )

    if radius <= 0:
        raise ValueError(
            "Radius must be greater than zero."
        )

    # --------------------------------------------------------
    # Initialize Earth Engine
    # --------------------------------------------------------

    try:
        init_gee()

    except Exception as exc:
        raise RuntimeError(
            "Google Earth Engine initialization failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Create analysis region
    # --------------------------------------------------------

    point = ee.Geometry.Point(
        [
            longitude,
            latitude,
        ]
    )

    region = point.buffer(
        radius
    )

    # --------------------------------------------------------
    # Sentinel-2 collection
    # --------------------------------------------------------

    collection = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(region)
        .filterDate(
            "2024-01-01",
            "2025-01-01",
        )
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                20,
            )
        )
        .sort(
            "CLOUDY_PIXEL_PERCENTAGE"
        )
    )

    # --------------------------------------------------------
    # Check imagery availability
    # --------------------------------------------------------

    image_count = collection.size().getInfo()

    if image_count == 0:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius,

            "vegetation_percent": 0.0,
            "water_percent": 0.0,
            "builtup_percent": 0.0,
            "barren_percent": 0.0,

            "suitability_score": 0,
            "recommended_use": "No Data",
            "confidence": 0.0,

            "image_count": 0,

            "message": (
                "No suitable Sentinel-2 imagery "
                "was found for the selected location."
            ),
        }

    # --------------------------------------------------------
    # Select least-cloudy suitable image
    # --------------------------------------------------------

    image = collection.first()

    if image is None:
        raise RuntimeError(
            "Unable to select a Sentinel-2 image."
        )

    # --------------------------------------------------------
    # Calculate spectral indices
    # --------------------------------------------------------

    ndvi = (
        image
        .normalizedDifference(
            [
                "B8",
                "B4",
            ]
        )
        .rename("NDVI")
    )

    ndwi = (
        image
        .normalizedDifference(
            [
                "B3",
                "B8",
            ]
        )
        .rename("NDWI")
    )

    ndbi = (
        image
        .normalizedDifference(
            [
                "B11",
                "B8",
            ]
        )
        .rename("NDBI")
    )

    # --------------------------------------------------------
    # Pixel area
    # --------------------------------------------------------

    pixel_area = ee.Image.pixelArea()

    # --------------------------------------------------------
    # Land-cover masks
    # --------------------------------------------------------

    vegetation_mask = (
        ndvi.gt(0.4)
        .And(
            ndwi.lte(0.2)
        )
    )

    water_mask = ndwi.gt(
        0.2
    )

    builtup_mask = (
        ndbi.gt(0.2)
        .And(
            ndvi.lt(0.4)
        )
        .And(
            ndwi.lte(0.2)
        )
    )

    # Barren land:
    # low vegetation + low water + low built-up
    barren_mask = (
        ndvi.lte(0.4)
        .And(
            ndwi.lte(0.2)
        )
        .And(
            ndbi.lte(0.2)
        )
    )

    # --------------------------------------------------------
    # Calculate all areas together
    # --------------------------------------------------------

    area_image = ee.Image.cat(
        [
            pixel_area
            .rename("total_area"),

            pixel_area
            .updateMask(
                vegetation_mask
            )
            .rename("vegetation_area"),

            pixel_area
            .updateMask(
                water_mask
            )
            .rename("water_area"),

            pixel_area
            .updateMask(
                builtup_mask
            )
            .rename("builtup_area"),

            pixel_area
            .updateMask(
                barren_mask
            )
            .rename("barren_area"),
        ]
    )

    area_values = (
        area_image
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e8,
            bestEffort=True,
        )
        .getInfo()
    )

    if not area_values:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "suitability statistics."
        )

    # --------------------------------------------------------
    # Extract area values
    # --------------------------------------------------------

    total_area_m2 = float(
        area_values.get(
            "total_area",
            0.0,
        )
        or 0.0
    )

    vegetation_m2 = float(
        area_values.get(
            "vegetation_area",
            0.0,
        )
        or 0.0
    )

    water_m2 = float(
        area_values.get(
            "water_area",
            0.0,
        )
        or 0.0
    )

    builtup_m2 = float(
        area_values.get(
            "builtup_area",
            0.0,
        )
        or 0.0
    )

    barren_m2 = float(
        area_values.get(
            "barren_area",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # Use geometric area if pixel-area result is unavailable
    # --------------------------------------------------------

    if total_area_m2 <= 0:

        total_area_m2 = (
            math.pi
            * (radius ** 2)
        )

    # --------------------------------------------------------
    # Convert to percentages
    # --------------------------------------------------------

    vegetation_pct = (
        vegetation_m2
        / total_area_m2
        * 100
    )

    water_pct = (
        water_m2
        / total_area_m2
        * 100
    )

    builtup_pct = (
        builtup_m2
        / total_area_m2
        * 100
    )

    barren_pct = (
        barren_m2
        / total_area_m2
        * 100
    )

    # --------------------------------------------------------
    # Keep percentages within valid range
    # --------------------------------------------------------

    vegetation_pct = max(
        0.0,
        min(
            100.0,
            vegetation_pct,
        ),
    )

    water_pct = max(
        0.0,
        min(
            100.0,
            water_pct,
        ),
    )

    builtup_pct = max(
        0.0,
        min(
            100.0,
            builtup_pct,
        ),
    )

    barren_pct = max(
        0.0,
        min(
            100.0,
            barren_pct,
        ),
    )

    # --------------------------------------------------------
    # Suitability recommendation
    # --------------------------------------------------------

    if vegetation_pct > 60:
        recommendation = "Agriculture"
        score = 95

    elif barren_pct > 50:
        recommendation = "Afforestation"
        score = 88

    elif builtup_pct > 40:
        recommendation = "Urban Development"
        score = 90

    elif water_pct > 20:
        recommendation = "Water Conservation"
        score = 87

    else:
        recommendation = "Mixed Land Use"
        score = 75

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = round(
        score / 100,
        2,
    )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,

        "vegetation_percent": round(
            vegetation_pct,
            2,
        ),

        "water_percent": round(
            water_pct,
            2,
        ),

        "builtup_percent": round(
            builtup_pct,
            2,
        ),

        "barren_percent": round(
            barren_pct,
            2,
        ),

        "suitability_score": score,

        "recommended_use": recommendation,

        "confidence": confidence,

        "image_count": image_count,

        "message": (
            "Land suitability analysis "
            "completed successfully."
        ),
    }
