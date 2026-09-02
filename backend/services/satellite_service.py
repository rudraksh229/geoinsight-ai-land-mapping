import ee

ee.Initialize(project="geoinsight-ai-503616")


def get_satellite_image(latitude, longitude, radius):

    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate("2024-01-01", "2024-12-31")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
        .first()
    )

    rgb = image.select(["B4", "B3", "B2"])

    url = rgb.getThumbURL({
        "region": region,
        "dimensions": 1024,
        "format": "png",
        "min": 0,
        "max": 3000
    })

    return {
        "image_url": url
    }
