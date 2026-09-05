import math

import ee

from gee_config import init_gee


# ============================================================
# BUILT-UP / URBAN LAND ANALYSIS
# ============================================================

def builtup_analysis(
    latitude,
    longitude,
    radius,
):
    """
    Estimate built-up / urban land using Sentinel-2 NDBI.

    This is a threshold-based analysis service.
    The primary AI classification is performed separately
    through the XGBoost pipeline in /mapping/analyze.
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
    # Initialize Google Earth Engine
    # --------------------------------------------------------

    try:
        init_gee()

    except Exception as exc:
        raise RuntimeError(
            "Google Earth Engine initialization failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Create region
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
    )

    # --------------------------------------------------------
    # Check imagery availability
    # --------------------------------------------------------

    image_count = collection.size().getInfo()

    if image_count == 0:
        return {
            "success": False,
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius,
            "total_area_ha": 0.0,
            "builtup_area_ha": 0.0,
            "builtup_percentage": 0.0,
            "ndbi": None,
            "ndvi": None,
            "ndwi": None,
            "image_count": 0,
            "message": (
                "No suitable Sentinel-2 imagery "
                "was found for the selected location."
            ),
        }

    # --------------------------------------------------------
    # Create median composite
    # --------------------------------------------------------

    image = collection.median()

    # --------------------------------------------------------
    # NDBI
    #
    # NDBI = (SWIR - NIR) / (SWIR + NIR)
    #
    # Sentinel-2:
    # B11 = SWIR
    # B8  = NIR
    # --------------------------------------------------------

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
    # NDVI
    #
    # Used to prevent highly vegetated areas from being
    # incorrectly counted as built-up.
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

    # --------------------------------------------------------
    # NDWI
    #
    # Used to exclude water bodies.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Built-up mask
    #
    # NDBI > 0.2
    # NDVI < 0.4
    # NDWI <= 0.2
    # --------------------------------------------------------

    builtup_mask = (
        ndbi.gt(0.2)
        .And(
            ndvi.lt(0.4)
        )
        .And(
            ndwi.lte(0.2)
        )
    )

    # --------------------------------------------------------
    # Pixel area
    # --------------------------------------------------------

    pixel_area = ee.Image.pixelArea()

    builtup_area_image = (
        pixel_area
        .updateMask(
            builtup_mask
        )
        .rename(
            "builtup_area"
        )
    )

    # --------------------------------------------------------
    # Calculate mean indices
    # --------------------------------------------------------

    statistics = (
        ee.Image.cat(
            [
                ndbi,
                ndvi,
                ndwi,
            ]
        )
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e8,
            bestEffort=True,
        )
        .getInfo()
    )

    if not statistics:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "built-up statistics."
        )

    # --------------------------------------------------------
    # Calculate built-up area
    # --------------------------------------------------------

    builtup_area_result = (
        builtup_area_image
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e8,
            bestEffort=True,
        )
        .getInfo()
    )

    if not builtup_area_result:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "built-up area statistics."
        )

    builtup_area_m2 = float(
        builtup_area_result.get(
            "builtup_area",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # Convert m² → hectares
    # --------------------------------------------------------

    builtup_area_ha = (
        builtup_area_m2 / 10000
    )

    # --------------------------------------------------------
    # Total circular region area
    # --------------------------------------------------------

    total_area_ha = (
        math.pi
        * (radius ** 2)
        / 10000
    )

    # --------------------------------------------------------
    # Calculate percentage
    # --------------------------------------------------------

    if total_area_ha > 0:
        builtup_percentage = (
            builtup_area_ha
            / total_area_ha
            * 100
        )

    else:
        builtup_percentage = 0.0

    builtup_percentage = max(
        0.0,
        min(
            100.0,
            builtup_percentage,
        ),
    )

    # --------------------------------------------------------
    # Extract index values
    # --------------------------------------------------------

    average_ndbi = statistics.get(
        "NDBI"
    )

    average_ndvi = statistics.get(
        "NDVI"
    )

    average_ndwi = statistics.get(
        "NDWI"
    )

    # --------------------------------------------------------
    # Convert safely
    # --------------------------------------------------------

    average_ndbi = (
        float(average_ndbi)
        if average_ndbi is not None
        else None
    )

    average_ndvi = (
        float(average_ndvi)
        if average_ndvi is not None
        else None
    )

    average_ndwi = (
        float(average_ndwi)
        if average_ndwi is not None
        else None
    )

    # --------------------------------------------------------
    # Round values
    # --------------------------------------------------------

    total_area_ha = round(
        total_area_ha,
        2,
    )

    builtup_area_ha = round(
        builtup_area_ha,
        2,
    )

    builtup_percentage = round(
        builtup_percentage,
        2,
    )

    if average_ndbi is not None:
        average_ndbi = round(
            average_ndbi,
            4,
        )

    if average_ndvi is not None:
        average_ndvi = round(
            average_ndvi,
            4,
        )

    if average_ndwi is not None:
        average_ndwi = round(
            average_ndwi,
            4,
        )

    # --------------------------------------------------------
    # Built-up intensity
    # --------------------------------------------------------

    if builtup_percentage >= 50:
        builtup_status = "High Built-up Presence"

    elif builtup_percentage >= 25:
        builtup_status = "Moderate Built-up Presence"

    elif builtup_percentage > 0:
        builtup_status = "Low Built-up Presence"

    else:
        builtup_status = "No Significant Built-up Area"

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "success": True,

        "latitude": latitude,
        "longitude": longitude,

        "radius_meters": radius,

        "total_area_ha": total_area_ha,

        "builtup_area_ha": builtup_area_ha,

        "builtup_percentage": builtup_percentage,

        "ndbi": average_ndbi,

        "ndvi": average_ndvi,

        "ndwi": average_ndwi,

        "builtup_status": builtup_status,

        "image_count": image_count,

        "message": (
            "Built-up land analysis "
            "completed successfully."
        ),
    }
