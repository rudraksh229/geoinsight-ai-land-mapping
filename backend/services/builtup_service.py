import ee
from gee_config import init_gee


def detect_builtup(latitude, longitude, radius):
    # Lazy initialize GEE safely on execution
    init_gee()

    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate("2024-01-01", "2024-12-31")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
        .first()
    )

    ndbi = image.normalizedDifference(["B11", "B8"]).rename("NDBI")

    pixel_area = ee.Image.pixelArea()

    total_area = ee.Number(
        pixel_area.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        ).get("area")
    )

    builtup = ee.Number(
        pixel_area.updateMask(ndbi.gt(0.2))
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .get("area")
    )

    builtup_percent = builtup.divide(total_area).multiply(100)

    percent = builtup_percent.getInfo()

    if percent > 40:
        status = "Highly Urbanized"
    elif percent > 15:
        status = "Moderately Urbanized"
    else:
        status = "Low Urbanization"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "builtup_area_ha": round(builtup.divide(10000).getInfo(), 2),
        "builtup_percentage": round(percent, 2),
        "status": status,
    }
    