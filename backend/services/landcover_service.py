import ee


# ==========================================
# EARTH ENGINE INITIALIZATION
# ==========================================

try:
    ee.Initialize(project="geoinsight-ai-503616")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="geoinsight-ai-503616")


# ==========================================
# LAND COVER CLASSIFICATION
# ==========================================

def classify_landcover(latitude: float, longitude: float, radius: int):

    point = ee.Geometry.Point([
        longitude,
        latitude
    ])

    region = point.buffer(radius)

    # ==========================================
    # SENTINEL-2
    # ==========================================

    collection = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(region)
        .filterDate(
            "2024-01-01",
            "2024-12-31"
        )
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                20
            )
        )
    )

    # Check collection
    if collection.size().getInfo() == 0:
        raise Exception(
            "No Sentinel-2 imagery found for this location."
        )

    image = collection.median().clip(region)

    # ==========================================
    # SPECTRAL INDICES
    # ==========================================

    ndvi = image.normalizedDifference(
        ["B8", "B4"]
    ).rename("NDVI")

    ndwi = image.normalizedDifference(
        ["B3", "B8"]
    ).rename("NDWI")

    ndbi = image.normalizedDifference(
        ["B11", "B8"]
    ).rename("NDBI")

    # ==========================================
    # LAND COVER RULES
    # ==========================================

    water_mask = ndwi.gt(0.2)

    vegetation_mask = (
        ndvi.gt(0.4)
        .And(water_mask.Not())
    )

    builtup_mask = (
        ndbi.gt(0.2)
        .And(water_mask.Not())
        .And(vegetation_mask.Not())
    )

    # Moderate NDVI areas are treated as agriculture
    agriculture_mask = (
        ndvi.gte(0.2)
        .And(ndvi.lte(0.4))
        .And(water_mask.Not())
        .And(builtup_mask.Not())
    )

    # Remaining land = barren
    barren_mask = (
        water_mask.Not()
        .And(vegetation_mask.Not())
        .And(builtup_mask.Not())
        .And(agriculture_mask.Not())
    )

    # ==========================================
    # CLASS IMAGE
    #
    # 1 = Vegetation
    # 2 = Agriculture
    # 3 = Built-up
    # 4 = Barren
    # 5 = Water
    # ==========================================

    classified = (
        ee.Image(0)
        .where(vegetation_mask, 1)
        .where(agriculture_mask, 2)
        .where(builtup_mask, 3)
        .where(barren_mask, 4)
        .where(water_mask, 5)
        .rename("class_id")
        .clip(region)
    )

    # ==========================================
    # PIXEL AREA
    # ==========================================

    pixel_area = ee.Image.pixelArea().rename("area")

    classified_with_area = classified.addBands(
        pixel_area
    )

    # ==========================================
    # VECTORIZE CLASSIFICATION
    # ==========================================

    vectors = classified_with_area.reduceToVectors(
        geometry=region,
        scale=20,
        geometryType="polygon",
        reducer=ee.Reducer.sum(),
        labelProperty="class_id",
        maxPixels=1e9,
        bestEffort=True,
        tileScale=4
    )

    vector_data = vectors.getInfo()

    # ==========================================
    # CLASS INFORMATION
    # ==========================================

    class_info = {
        1: {
            "type": "vegetation",
            "label": "Vegetation",
            "color": "#22c55e"
        },
        2: {
            "type": "agriculture",
            "label": "Agricultural Land",
            "color": "#eab308"
        },
        3: {
            "type": "built-up",
            "label": "Built-up",
            "color": "#6b7280"
        },
        4: {
            "type": "barren",
            "label": "Barren Land",
            "color": "#a16207"
        },
        5: {
            "type": "water",
            "label": "Water Bodies",
            "color": "#3b82f6"
        }
    }

    # ==========================================
    # BUILD GEOJSON FEATURES
    # ==========================================

    features = []

    area_totals = {
        "vegetation": 0,
        "agriculture": 0,
        "builtup": 0,
        "barren": 0,
        "water": 0
    }

    for feature in vector_data.get("features", []):

        properties = feature.get(
            "properties",
            {}
        )

        class_id = int(
            properties.get(
                "class_id",
                0
            )
        )

        if class_id not in class_info:
            continue

        info = class_info[class_id]

        # reduceToVectors returns pixel-area sum
        area_m2 = float(
            properties.get(
                "sum",
                0
            )
        )

        area_ha = round(
            area_m2 / 10000,
            2
        )

        if area_ha <= 0:
            continue

        area_totals[
            info["type"].replace(
                "-",
                ""
            )
        ] += area_ha

        features.append({

            "type": "Feature",

            "geometry": feature.get(
                "geometry"
            ),

            "properties": {

                "class_id": class_id,

                "type": info["type"],

                "label": info["label"],

                "area": f"{area_ha:.2f} Ha",

                "area_ha": area_ha,

                "color": info["color"]

            }

        })

    # ==========================================
    # TOTAL AREA
    # ==========================================

    total_area = round(
        math_pi_area(radius),
        2
    )

    return {

        "latitude": latitude,

        "longitude": longitude,

        "radius_meters": radius,

        "vegetation_ha": round(
            area_totals["vegetation"],
            2
        ),

        "agriculture_ha": round(
            area_totals["agriculture"],
            2
        ),

        "water_ha": round(
            area_totals["water"],
            2
        ),

        "builtup_ha": round(
            area_totals["builtup"],
            2
        ),

        "barren_ha": round(
            area_totals["barren"],
            2
        ),

        "total_area_ha": total_area,

        "mapData": {

            "type": "FeatureCollection",

            "features": features

        }

    }


# ==========================================
# CIRCLE AREA
# ==========================================

def math_pi_area(radius):

    import math

    return (
        math.pi *
        (radius ** 2) /
        10000
    )
    