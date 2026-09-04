import ee
from gee_config import init_gee


def detect_water(latitude, longitude, radius):
    # Safe lazy initialization on execution
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

    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")

    pixel_area = ee.Image.pixelArea()

    total_area = ee.Number(
        pixel_area.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        ).get("area")
    )

    water = ee.Number(
        pixel_area.updateMask(ndwi.gt(0.2))
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .get("area")
    )

    water_percent_num = water.divide(total_area).multiply(100)
    
    # Store fetched values once to avoid multiple blocking GEE network calls
    percent = water_percent_num.getInfo()
    water_area_ha = round(water.divide(10000).getInfo(), 2)

    if percent > 40:
        status = "High Water Presence"
    elif percent > 15:
        status = "Moderate Water Presence"
    else:
        status = "Low Water Presence"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "water_area_ha": water_area_ha,
        "water_percentage": round(percent, 2),
        "status": status,
    }
    