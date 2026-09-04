import ee
from gee_config import init_gee


def analyze_suitability(latitude, longitude, radius):
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

    ndvi = image.normalizedDifference(["B8", "B4"])
    ndwi = image.normalizedDifference(["B3", "B8"])
    ndbi = image.normalizedDifference(["B11", "B8"])

    pixel_area = ee.Image.pixelArea()

    total_area = ee.Number(
        pixel_area.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        ).get("area")
    )

    vegetation = ee.Number(
        pixel_area.updateMask(ndvi.gt(0.4))
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e13,
        )
        .get("area")
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

    barren = total_area.subtract(
        vegetation.add(water).add(builtup)
    )

    vegetation_pct = vegetation.divide(total_area).multiply(100).getInfo()
    water_pct = water.divide(total_area).multiply(100).getInfo()
    builtup_pct = builtup.divide(total_area).multiply(100).getInfo()
    barren_pct = barren.divide(total_area).multiply(100).getInfo()

    # AI Suitability Logic
    if vegetation_pct > 60:
        recommendation = "Agriculture"
        score = 95

    elif barren_pct > 50:
        recommendation = "Afforestation"
        score = 88

    elif builtup_pct > 40:
        recommendation = "Urban Development"
        score = 90

    elif water_pct > 20:
        recommendation = "Water Conservation"
        score = 87

    else:
        recommendation = "Mixed Land Use"
        score = 75

    confidence = round(score / 100, 2)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,

        "vegetation_percent": round(vegetation_pct, 2),
        "water_percent": round(water_pct, 2),
        "builtup_percent": round(builtup_pct, 2),
        "barren_percent": round(barren_pct, 2),

        "suitability_score": score,
        "recommended_use": recommendation,
        "confidence": confidence,
    }
    