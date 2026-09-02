import ee

ee.Initialize(project="geoinsight-ai-503616")


def detect_water(latitude, longitude, radius):

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

    water_percent = water.divide(total_area).multiply(100)

    if water_percent.getInfo() > 40:
        status = "High Water Presence"
    elif water_percent.getInfo() > 15:
        status = "Moderate Water Presence"
    else:
        status = "Low Water Presence"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "water_area_ha": round(water.divide(10000).getInfo(), 2),
        "water_percentage": round(water_percent.getInfo(), 2),
        "status": status,
    }
