import ee

ee.Initialize(project="geoinsight-ai-503616")


def detect_barren_land(latitude, longitude, radius):

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
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    ndbi = image.normalizedDifference(["B11", "B8"]).rename("NDBI")

    pixel_area = ee.Image.pixelArea()

    barren_mask = (
        ndvi.lt(0.2)
        .And(ndwi.lt(0.1))
        .And(ndbi.lt(0.2))
    )

    barren_area = (
        pixel_area.updateMask(barren_mask)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .get("area")
    )

    total_area = (
        pixel_area.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .get("area")
    )

    barren_area = ee.Number(barren_area)
    total_area = ee.Number(total_area)

    percentage = barren_area.divide(total_area).multiply(100)

    if percentage.getInfo() > 60:
        status = "Highly Barren"
    elif percentage.getInfo() > 30:
        status = "Moderately Barren"
    else:
        status = "Low Barren Area"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "barren_area_ha": round(barren_area.divide(10000).getInfo(), 2),
        "barren_percentage": round(percentage.getInfo(), 2),
        "status": status,
    }
