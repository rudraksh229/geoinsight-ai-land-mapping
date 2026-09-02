import ee

ee.Initialize(project="geoinsight-ai-503616")


def vegetation_health(latitude, longitude, radius):
    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate("2024-01-01", "2024-12-31")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
        .first()
    )

    # Calculate NDVI
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    # Mean NDVI
    mean_ndvi = (
        ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .get("NDVI")
    )

    mean_ndvi = ee.Number(mean_ndvi)

    # Vegetation Area (NDVI > 0.4)
    vegetation_mask = ndvi.gt(0.4)

    vegetation_area = (
        ee.Image.pixelArea()
        .updateMask(vegetation_mask)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .get("area")
    )

    vegetation_area = ee.Number(vegetation_area)

    total_area = ee.Number(region.area())

    vegetation_percent = (
        vegetation_area.divide(total_area)
        .multiply(100)
    )

    # Health Classification
    ndvi_value = mean_ndvi.getInfo()

    if ndvi_value >= 0.6:
        health = "Excellent"

    elif ndvi_value >= 0.4:
        health = "Good"

    elif ndvi_value >= 0.2:
        health = "Moderate"

    else:
        health = "Poor"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "average_ndvi": round(ndvi_value, 3),
        "vegetation_percent": round(
            vegetation_percent.getInfo(), 2
        ),
        "vegetation_health": health,
    }
