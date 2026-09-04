import ee
from gee_config import init_gee

def extract_features(latitude, longitude, radius):
    # Earth Engine initialize yahan call karein
    init_gee()

    point = ee.Geometry.Point([longitude, latitude])
    roi = point.buffer(radius)

    # Sentinel-2 image
    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate("2024-01-01", "2024-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .median()
    )

    # Check image
    if image.bandNames().size().getInfo() == 0:
        raise Exception("No Sentinel-2 image found for this location.")

    # Spectral indices
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    ndbi = image.normalizedDifference(["B11", "B8"]).rename("NDBI")

    savi = image.expression(
        "1.5*((nir-red)/(nir+red+0.5))",
        {"nir": image.select("B8"), "red": image.select("B4")}
    ).rename("SAVI")

    evi = image.expression(
        "2.5*((nir-red)/(nir+6*red-7.5*blue+1))",
        {
            "nir": image.select("B8"),
            "red": image.select("B4"),
            "blue": image.select("B2")
        }
    ).rename("EVI")

    bsi = image.expression(
        "((swir+red)-(nir+blue))/((swir+red)+(nir+blue))",
        {
            "swir": image.select("B11"),
            "red": image.select("B4"),
            "nir": image.select("B8"),
            "blue": image.select("B2")
        }
    ).rename("BSI")

    # Terrain
    terrain = ee.Terrain.products(ee.Image("USGS/SRTMGL1_003"))

    aspect = terrain.select("aspect")
    elevation = terrain.select("elevation")
    slope = terrain.select("slope")

    # Stack exactly like training
    stack = ee.Image.cat([
        aspect.rename("Aspect"),
        image.select("B11"),
        image.select("B12"),
        image.select("B2"),
        image.select("B3"),
        image.select("B4"),
        image.select("B8"),
        bsi,
        evi,
        elevation.rename("Elevation"),
        ndbi,
        ndvi,
        ndwi,
        savi,
        slope.rename("Slope")
    ])

    values = stack.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=10,
        maxPixels=1e9
    ).getInfo()

    feature_order = [
        "Aspect", "B11", "B12", "B2", "B3", "B4", "B8",
        "BSI", "EVI", "Elevation", "NDBI", "NDVI", "NDWI", "SAVI", "Slope"
    ]

    features = []

    for feature in feature_order:
        value = values.get(feature)
        if value is None:
            value = 0
        features.append(float(value))

    return {
        "feature_vector": features,
        "statistics": {
            "Aspect": values.get("Aspect", 0),
            "Elevation": values.get("Elevation", 0),
            "Slope": values.get("Slope", 0),
            "NDVI": values.get("NDVI", 0),
            "NDWI": values.get("NDWI", 0),
            "NDBI": values.get("NDBI", 0),
        },
        "features": {
            "B2": values.get("B2", 0),
            "B3": values.get("B3", 0),
            "B4": values.get("B4", 0),
            "B8": values.get("B8", 0),
            "B11": values.get("B11", 0),
            "B12": values.get("B12", 0),
            "BSI": values.get("BSI", 0),
            "EVI": values.get("EVI", 0),
            "SAVI": values.get("SAVI", 0),
        }
    }
    