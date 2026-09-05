import ee

from gee_config import init_gee


# ============================================================
# NDVI MAP TILE SERVICE
# ============================================================

def get_ndvi_tiles(
    latitude,
    longitude,
    radius,
):
    """
    Generate an NDVI visualization tile URL for the
    selected geographic region using Sentinel-2 imagery.
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
    # Calculate NDVI
    # --------------------------------------------------------

    ndvi = (
        image
        .normalizedDifference(
            [
                "B8",
                "B4",
            ]
        )
        .rename(
            "NDVI"
        )
    )

    # --------------------------------------------------------
    # Visualization parameters
    # --------------------------------------------------------

    visualization = {
        "min": 0,
        "max": 1,
        "palette": [
            "white",
            "yellow",
            "orange",
            "green",
            "darkgreen",
        ],
    }

    # --------------------------------------------------------
    # Generate Earth Engine map tiles
    # --------------------------------------------------------

    try:
        map_id = ndvi.getMapId(
            visualization
        )

        tile_fetcher = map_id.get(
            "tile_fetcher"
        )

        if tile_fetcher is None:
            raise RuntimeError(
                "Earth Engine did not return a tile fetcher."
            )

        tile_url = (
            tile_fetcher.url_format
        )

    except Exception as exc:
        raise RuntimeError(
            "Failed to generate NDVI map tiles. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "success": True,

        "tile_url": tile_url,

        "center": {
            "latitude": latitude,
            "longitude": longitude,
        },

        "radius": radius,

        "layer": "NDVI",

        "image_count": image_count,

        "message": (
            "NDVI map tiles generated successfully."
        ),
    }
