import ee

PROJECT_ID = "geoinsight-ai-503616"


def initialize_gee():
    """
    Initialize Google Earth Engine.
    """
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)


def get_map_metadata():
    """
    Returns basic metadata about Sentinel-2 imagery.
    """

    initialize_gee()

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterDate("2024-01-01", "2024-12-31")
        .filterBounds(
            ee.Geometry.Point([77.4126, 23.2599])  # Bhopal
        )
        .sort("CLOUDY_PIXEL_PERCENTAGE")
    )

    image = collection.first()

    return {
        "dataset": "Sentinel-2 Surface Reflectance",
        "imageCount": collection.size().getInfo(),
        "bands": image.bandNames().getInfo(),
        "imageId": image.get("PRODUCT_ID").getInfo(),
    }