import ee

ee.Initialize(project="geoinsight-ai-503616")


def detect_change(latitude, longitude, radius, start_date, end_date):

    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    image1 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start_date, start_date[:4] + "-12-31")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
        .first()
    )

    image2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(end_date, end_date[:4] + "-12-31")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
        .first()
    )

    ndvi1 = image1.normalizedDifference(["B8", "B4"])
    ndvi2 = image2.normalizedDifference(["B8", "B4"])

    difference = ndvi2.subtract(ndvi1)

    avg_change = (
        difference.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .values()
        .get(0)
    )

    avg_change = ee.Number(avg_change).getInfo()

    if avg_change > 0.15:
        status = "Vegetation Increased"
    elif avg_change < -0.15:
        status = "Vegetation Decreased"
    else:
        status = "Minimal Change"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "start_date": start_date,
        "end_date": end_date,
        "average_ndvi_change": round(avg_change, 3),
        "status": status,
    }
