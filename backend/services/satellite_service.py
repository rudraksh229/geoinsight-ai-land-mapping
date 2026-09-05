import ee

from gee_config import init_gee


# ============================================================
# SATELLITE IMAGE SERVICE
# ============================================================

def get_satellite_image(
    latitude,
    longitude,
    radius,
):
    """
    Generate a Sentinel-2 RGB satellite-image thumbnail
    for the selected geographic region.
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
                30,
            )
        )
        .sort(
            "CLOUDY_PIXEL_PERCENTAGE"
        )
    )

    # --------------------------------------------------------
    # Check imagery availability
    # --------------------------------------------------------

    image_count = (
        collection
        .size()
        .getInfo()
    )

    if image_count == 0:
        raise RuntimeError(
            "No suitable Sentinel-2 imagery was found "
            "for the selected location."
        )

    # --------------------------------------------------------
    # Select best available image
    # --------------------------------------------------------

    image = collection.first()

    if image is None:
        raise RuntimeError(
            "Unable to select a suitable Sentinel-2 image."
        )

    # --------------------------------------------------------
    # RGB bands
    #
    # B4 = Red
    # B3 = Green
    # B2 = Blue
    # --------------------------------------------------------

    rgb = image.select(
        [
            "B4",
            "B3",
            "B2",
        ]
    )

    # --------------------------------------------------------
    # Generate thumbnail
    # --------------------------------------------------------

    try:
        image_url = rgb.getThumbURL(
            {
                "region": region,
                "dimensions": 1024,
                "format": "png",
                "min": 0,
                "max": 3000,
            }
        )

    except Exception as exc:
        raise RuntimeError(
            "Failed to generate satellite-image thumbnail. "
            f"Reason: {exc}"
        ) from exc

    if not image_url:
        raise RuntimeError(
            "Earth Engine returned an empty satellite-image URL."
        )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "success": True,

        "image_url": image_url,

        "center": {
            "latitude": latitude,
            "longitude": longitude,
        },

        "radius": radius,

        "image_count": image_count,

        "layer": "Sentinel-2 RGB",

        "message": (
            "Satellite image generated successfully."
        ),
    }
