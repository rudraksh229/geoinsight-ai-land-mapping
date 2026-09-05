import ee

from gee_config import init_gee


# ============================================================
# WATER BODY ANALYSIS
# ============================================================

def water_analysis(
    latitude,
    longitude,
    radius,
):
    """
    Detect water bodies using Sentinel-2 NDWI.

    This is a threshold-based water analysis service.
    The primary AI classification remains the XGBoost
    pipeline used by /mapping/analyze.
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
            "water_area_ha": 0.0,
            "water_percentage": 0.0,
            "ndwi": None,
            "image_count": 0,
            "message": (
                "No suitable Sentinel-2 imagery "
                "was found for the selected location."
            ),
        }

    # --------------------------------------------------------
    # Median composite
    # --------------------------------------------------------

    image = collection.median()

    # --------------------------------------------------------
    # Calculate NDWI
    #
    # NDWI = (Green - NIR) / (Green + NIR)
    #
    # Sentinel-2:
    # B3 = Green
    # B8 = NIR
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
    # Water mask
    # --------------------------------------------------------

    water_mask = ndwi.gt(
        0.2
    )

    # --------------------------------------------------------
    # Pixel area
    # --------------------------------------------------------

    pixel_area = ee.Image.pixelArea()

    water_area_image = (
        pixel_area
        .updateMask(
            water_mask
        )
        .rename(
            "water_area"
        )
    )

    # --------------------------------------------------------
    # Calculate NDWI statistics
    # --------------------------------------------------------

    statistics = (
        ndwi
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
            "water statistics."
        )

    # --------------------------------------------------------
    # Calculate water area
    # --------------------------------------------------------

    water_area_result = (
        water_area_image
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e8,
            bestEffort=True,
        )
        .getInfo()
    )

    if not water_area_result:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "water-area statistics."
        )

    water_area_m2 = float(
        water_area_result.get(
            "water_area",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # Convert square meters → hectares
    # --------------------------------------------------------

    water_area_ha = (
        water_area_m2 / 10000
    )

    # --------------------------------------------------------
    # Calculate total circular area
    # --------------------------------------------------------

    import math

    total_area_ha = (
        math.pi
        * (radius ** 2)
        / 10000
    )

    # --------------------------------------------------------
    # Calculate percentage
    # --------------------------------------------------------

    if total_area_ha > 0:
        water_percentage = (
            water_area_ha
            / total_area_ha
            * 100
        )
    else:
        water_percentage = 0.0

    # Prevent numerical rounding from producing
    # an impossible percentage.
    water_percentage = max(
        0.0,
        min(
            100.0,
            water_percentage,
        ),
    )

    # --------------------------------------------------------
    # Average NDWI
    # --------------------------------------------------------

    average_ndwi = statistics.get(
        "NDWI"
    )

    if average_ndwi is not None:
        average_ndwi = round(
            float(average_ndwi),
            4,
        )

    # --------------------------------------------------------
    # Round output
    # --------------------------------------------------------

    total_area_ha = round(
        total_area_ha,
        2,
    )

    water_area_ha = round(
        water_area_ha,
        2,
    )

    water_percentage = round(
        water_percentage,
        2,
    )

    # --------------------------------------------------------
    # Water condition
    # --------------------------------------------------------

    if average_ndwi is None:
        water_status = "No Data"

    elif average_ndwi >= 0.4:
        water_status = "High Water Presence"

    elif average_ndwi >= 0.2:
        water_status = "Moderate Water Presence"

    elif average_ndwi >= 0:
        water_status = "Low Water Presence"

    else:
        water_status = "Very Low Water Presence"

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "success": True,

        "latitude": latitude,
        "longitude": longitude,

        "radius_meters": radius,

        "total_area_ha": total_area_ha,

        "water_area_ha": water_area_ha,

        "water_percentage": water_percentage,

        "ndwi": average_ndwi,

        "water_status": water_status,

        "image_count": image_count,

        "message": (
            "Water body analysis "
            "completed successfully."
        ),
    }
