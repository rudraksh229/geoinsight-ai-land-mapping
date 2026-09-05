import ee

from gee_config import init_gee


# ============================================================
# LAND-COVER ANALYSIS
# ============================================================

def classify_landcover(
    latitude,
    longitude,
    radius,
):
    """
    Classify the selected region into:

        Vegetation
        Agriculture
        Water
        Built-up
        Barren

    This service uses Sentinel-2 spectral indices.

    NOTE:
    The main AI endpoint (/mapping/analyze) uses the
    trained XGBoost model. This endpoint remains a
    separate threshold-based land-cover analysis.
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

    init_gee()

    # --------------------------------------------------------
    # Region
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
    # Check imagery
    # --------------------------------------------------------

    image_count = collection.size().getInfo()

    if image_count == 0:
        raise RuntimeError(
            "No suitable Sentinel-2 imagery was found "
            "for the selected location."
        )

    # --------------------------------------------------------
    # Create median composite
    # --------------------------------------------------------

    image = collection.median()

    # --------------------------------------------------------
    # Spectral indices
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
    # Add indices together
    # --------------------------------------------------------

    index_image = ee.Image.cat(
        [
            ndvi,
            ndwi,
            ndbi,
        ]
    )

    # --------------------------------------------------------
    # Calculate mean indices
    # --------------------------------------------------------

    mean_values = (
        index_image
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e8,
            bestEffort=True,
        )
        .getInfo()
    )

    if not mean_values:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "land-cover statistics."
        )

    average_ndvi = float(
        mean_values.get(
            "NDVI",
            0.0,
        )
        or 0.0
    )

    average_ndwi = float(
        mean_values.get(
            "NDWI",
            0.0,
        )
        or 0.0
    )

    average_ndbi = float(
        mean_values.get(
            "NDBI",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # Pixel-area image
    # --------------------------------------------------------

    pixel_area = ee.Image.pixelArea()

    # --------------------------------------------------------
    # Masks
    # --------------------------------------------------------

    water_mask = ndwi.gt(0.2)

    vegetation_mask = (
        ndvi.gt(0.4)
        .And(
            ndwi.lte(0.2)
        )
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

    # Barren = low vegetation + low water + low built-up
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
    # Calculate areas in one reduceRegion call
    # --------------------------------------------------------

    area_image = ee.Image.cat(
        [
            pixel_area
            .updateMask(
                vegetation_mask
            )
            .rename("vegetation"),

            pixel_area
            .updateMask(
                water_mask
            )
            .rename("water"),

            pixel_area
            .updateMask(
                builtup_mask
            )
            .rename("builtup"),

            pixel_area
            .updateMask(
                barren_mask
            )
            .rename("barren"),
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
            "land-cover area statistics."
        )

    # --------------------------------------------------------
    # Convert m² → hectares
    # --------------------------------------------------------

    vegetation_ha = (
        float(
            area_values.get(
                "vegetation",
                0.0,
            )
            or 0.0
        )
        / 10000
    )

    water_ha = (
        float(
            area_values.get(
                "water",
                0.0,
            )
            or 0.0
        )
        / 10000
    )

    builtup_ha = (
        float(
            area_values.get(
                "builtup",
                0.0,
            )
            or 0.0
        )
        / 10000
    )

    barren_ha = (
        float(
            area_values.get(
                "barren",
                0.0,
            )
            or 0.0
        )
        / 10000
    )

    # --------------------------------------------------------
    # Total area
    # --------------------------------------------------------

    total_area_ha = (
        math_pi()
        * (radius ** 2)
        / 10000
    )

    total_area_ha = float(
        total_area_ha
    )

    # --------------------------------------------------------
    # Agriculture
    # --------------------------------------------------------
    #
    # Agriculture is estimated as vegetation that is not
    # already represented by water/built-up/barren masks.
    #
    # This is a threshold-based estimate, not the XGBoost
    # model used by /mapping/analyze.
    # --------------------------------------------------------

    classified_area = (
        vegetation_ha
        + water_ha
        + builtup_ha
        + barren_ha
    )

    agriculture_ha = max(
        0.0,
        total_area_ha
        - classified_area,
    )

    # --------------------------------------------------------
    # Round values
    # --------------------------------------------------------

    total_area_ha = round(
        total_area_ha,
        2,
    )

    vegetation_ha = round(
        vegetation_ha,
        2,
    )

    agriculture_ha = round(
        agriculture_ha,
        2,
    )

    water_ha = round(
        water_ha,
        2,
    )

    builtup_ha = round(
        builtup_ha,
        2,
    )

    barren_ha = round(
        barren_ha,
        2,
    )

    # --------------------------------------------------------
    # Percentages
    # --------------------------------------------------------

    if total_area_ha > 0:
        vegetation_percent = round(
            vegetation_ha
            / total_area_ha
            * 100,
            2,
        )

        agriculture_percent = round(
            agriculture_ha
            / total_area_ha
            * 100,
            2,
        )

        water_percent = round(
            water_ha
            / total_area_ha
            * 100,
            2,
        )

        builtup_percent = round(
            builtup_ha
            / total_area_ha
            * 100,
            2,
        )

        barren_percent = round(
            barren_ha
            / total_area_ha
            * 100,
            2,
        )

    else:
        vegetation_percent = 0.0
        agriculture_percent = 0.0
        water_percent = 0.0
        builtup_percent = 0.0
        barren_percent = 0.0

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "success": True,

        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
        },

        "total_area_ha": total_area_ha,

        "land_cover": {
            "vegetation": vegetation_ha,
            "agriculture": agriculture_ha,
            "water": water_ha,
            "builtup": builtup_ha,
            "barren": barren_ha,
        },

        "percentages": {
            "vegetation": vegetation_percent,
            "agriculture": agriculture_percent,
            "water": water_percent,
            "builtup": builtup_percent,
            "barren": barren_percent,
        },

        "indices": {
            "NDVI": round(
                average_ndvi,
                4,
            ),

            "NDWI": round(
                average_ndwi,
                4,
            ),

            "NDBI": round(
                average_ndbi,
                4,
            ),
        },

        "image_count": image_count,

        "message": (
            "Land-cover analysis completed "
            "successfully."
        ),
    }


# ============================================================
# AREA HELPER
# ============================================================

def math_pi():
    """
    Small helper kept here to avoid changing the existing
    service structure.
    """
    import math

    return math.pi
