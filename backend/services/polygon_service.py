import json
import ee

ee.Initialize(project="geoinsight-ai-503616")


def analyze_polygon(file_bytes):

    geojson = json.loads(file_bytes.decode())

    geometry = ee.Geometry(geojson["features"][0]["geometry"])

    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(geometry)
        .filterDate("2024-01-01", "2024-12-31")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
        .first()
    )

    ndvi = image.normalizedDifference(
        ["B8", "B4"]
    ).rename("NDVI")

    ndwi = image.normalizedDifference(
        ["B3", "B8"]
    ).rename("NDWI")

    ndbi = image.normalizedDifference(
        ["B11", "B8"]
    ).rename("NDBI")

    pixel_area = ee.Image.pixelArea()

    total = pixel_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e13
    ).get("area")

    vegetation = pixel_area.updateMask(
        ndvi.gt(0.4)
    ).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e13
    ).get("area")

    water = pixel_area.updateMask(
        ndwi.gt(0.2)
    ).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e13
    ).get("area")

    builtup = pixel_area.updateMask(
        ndbi.gt(0.2)
    ).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e13
    ).get("area")

    total = ee.Number(total)
    vegetation = ee.Number(vegetation)
    water = ee.Number(water)
    builtup = ee.Number(builtup)

    barren = total.subtract(
        vegetation.add(water).add(builtup)
    )

    mean_ndvi = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        maxPixels=1e13
    ).get("NDVI")

    return {
        "total_area_ha": total.divide(10000).getInfo(),
        "vegetation_ha": vegetation.divide(10000).getInfo(),
        "water_ha": water.divide(10000).getInfo(),
        "builtup_ha": builtup.divide(10000).getInfo(),
        "barren_ha": barren.divide(10000).getInfo(),
        "average_ndvi": ee.Number(mean_ndvi).getInfo()
    }
