import ee

from gee_config import init_gee


# ============================================================
# BARREN LAND ANALYSIS
# ============================================================

def barren_land_analysis(
    latitude,
    longitude,
    radius,
):
    """
    Estimate barren land using Sentinel-2 spectral indices.

    This is a threshold-based analysis service.
    The primary AI classification is still performed by
    the XGBoost model through /mapping/analyze.
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
    # Sentinel-2 imagery
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
            "barren_area_ha": 0.0,
            "barren_percentage": 0.0,
            "ndvi": None,
            "ndbi": None,
            "bsi": None,
            "image_count": 0,
            "message": (
                "No suitable Sentinel-2 imagery "
                "was found for the selected location."
            ),
        }

    # --------------------------------------------------------
    # Median satellite composite
    # --------------------------------------------------------

    image = collection.median()

    # --------------------------------------------------------
    # NDVI
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
    # NDBI
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
    # BSI
    #
    # BSI =
    # ((SWIR + RED) - (NIR + BLUE))
    # /
    # ((SWIR + RED) + (NIR + BLUE))
    # --------------------------------------------------------

    bsi = (
        image
        .expression(
            "((swir + red) - (nir + blue)) / "
            "((swir + red) + (nir + blue))",
            {
                "swir": image.select("B11"),
                "red": image.select("B4"),
                "nir": image.select("B8"),
                "blue": image.select("B2"),
            },
        )
        .rename("BSI")
    )

    # --------------------------------------------------------
    # NDWI
    #
    # Used to exclude water from barren classification.
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
    # Barren mask
    #
    # Low vegetation
    # High/positive bare-soil signal
    # Low water signal
    # Low built-up signal
    # --------------------------------------------------------

    barren_mask = (
        ndvi.lt(0.3)
        .And(
            bsi.gt(0.0)
        )
        .And(
            ndwi.lt(0.2)
        )
        .And(
            ndbi.lt(0.2)
        )
    )

    # --------------------------------------------------------
    # Calculate pixel area
    # --------------------------------------------------------

    pixel_area = ee.Image.pixelArea()

    barren_area_image = (
        pixel_area
        .updateMask(
            barren_mask
        )
        .rename(
            "barren_area"
        )
    )

    # --------------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------------

    statistics_image = ee.Image.cat(
        [
            ndvi,
            ndwi,
            ndbi,
            bsi,
        ]
    )

    statistics = (
        statistics_image
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
            "barren-land statistics."
        )

    # --------------------------------------------------------
    # Calculate barren area
    # --------------------------------------------------------

    barren_area_result = (
        barren_area_image
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e8,
            bestEffort=True,
        )
        .getInfo()
    )

    if not barren_area_result:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "barren-land area data."
        )

    barren_area_m2 = float(
        barren_area_result.get(
            "barren_area",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # Convert m² → hectares
    # --------------------------------------------------------

    barren_area_ha = (
        barren_area_m2 / 10000
    )

    # --------------------------------------------------------
    # Total circular region area
    # --------------------------------------------------------

    import math

    total_area_ha = (
        math.pi
        * (radius ** 2)
        / 10000
    )

    # --------------------------------------------------------
    # Percentage
    # --------------------------------------------------------

    if total_area_ha > 0:
        barren_percentage = (
            barren_area_ha
            / total_area_ha
            * 100
        )
    else:
        barren_percentage = 0.0

    # --------------------------------------------------------
    # Extract indices safely
    # --------------------------------------------------------

    average_ndvi = statistics.get(
        "NDVI"
    )

    average_ndwi = statistics.get(
        "NDWI"
    )

    average_ndbi = statistics.get(
        "NDBI"
    )

    average_bsi = statistics.get(
        "BSI"
    )

    # --------------------------------------------------------
    # Convert values
    # --------------------------------------------------------

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

    average_ndbi = (
        float(average_ndbi)
        if average_ndbi is not None
        else None
    )

    average_bsi = (
        float(average_bsi)
        if average_bsi is not None
        else None
    )

    # --------------------------------------------------------
    # Round values
    # --------------------------------------------------------

    total_area_ha = round(
        total_area_ha,
        2,
    )

    barren_area_ha = round(
        barren_area_ha,
        2,
    )

    barren_percentage = round(
        barren_percentage,
        2,
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

    if average_ndbi is not None:
        average_ndbi = round(
            average_ndbi,
            4,
        )

    if average_bsi is not None:
        average_bsi = round(
            average_bsi,
            4,
        )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "success": True,

        "latitude": latitude,
        "longitude": longitude,

        "radius_meters": radius,

        "total_area_ha": total_area_ha,

        "barren_area_ha": barren_area_ha,

        "barren_percentage": barren_percentage,

        "indices": {
            "NDVI": average_ndvi,
            "NDWI": average_ndwi,
            "NDBI": average_ndbi,
            "BSI": average_bsi,
        },

        "image_count": image_count,

        "message": (
            "Barren land analysis "
            "completed successfully."
        ),
    }
