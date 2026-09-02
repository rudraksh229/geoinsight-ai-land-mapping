import ee

ee.Initialize(project="geoinsight-ai-503616")


def get_ndvi_tiles(latitude, longitude, radius):

    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate("2024-01-01", "2024-12-31")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
        .first()
    )

    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    vis = {
        "min": 0,
        "max": 1,
        "palette": [
            "white",
            "yellow",
            "orange",
            "green",
            "darkgreen"
        ]
    }

    map_id = ndvi.getMapId(vis)

    return {
        "tile_url": map_id["tile_fetcher"].url_format,
        "center": {
            "latitude": latitude,
            "longitude": longitude
        },
        "radius": radius,
        "layer": "NDVI"
    }
