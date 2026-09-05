
import json

import ee

from gee_config import init_gee


def analyze_polygon(file_bytes):
    """
    Analyze a GeoJSON polygon using Sentinel-2 imagery
    and calculate land-cover statistics.
    """

    init_gee()

    if not file_bytes:
        raise ValueError(
            "Uploaded polygon file is empty."
        )

    try:
        geojson = json.loads(
            file_bytes.decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "Invalid GeoJSON file."
        ) from exc

    if not isinstance(geojson, dict):
        raise ValueError(
            "Invalid GeoJSON structure."
        )

    features = geojson.get("features")

    if not features:
        raise ValueError(
            "GeoJSON does not contain any features."
        )

    geometry_data = features[0].get(
        "geometry"
    )

    if not geometry_data:
        raise ValueError(
            "GeoJSON feature does not contain geometry."
        )

    geometry_type = geometry_data.get(
        "type"
    )

    if geometry_type not in {
        "Polygon",
        "MultiPolygon",
    }:
        raise ValueError(
            "Only Polygon and MultiPolygon geometries are supported."
        )

    try:
        geometry = ee.Geometry(
            geometry_data
        )

        image = (
            ee.ImageCollection(
                "COPERNICUS/S2_SR_HARMONIZED"
            )
            .filterBounds(geometry)
            .filterDate(
                "2024-01-01",
                "2025-01-01",
            )
            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    20,
                )
            )
            .sort(
                "CLOUDY_PIXEL_PERCENTAGE"
            )
            .first()
        )

        image_info = image.getInfo()

        if not image_info:
            raise ValueError(
                "No suitable Sentinel-2 imagery was found for the uploaded polygon."
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
            maxPixels=1e13,
        ).get("area")

        vegetation = pixel_area.updateMask(
            ndvi.gt(0.4)
        ).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e13,
        ).get("area")

        water = pixel_area.updateMask(
            ndwi.gt(0.2)
        ).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e13,
        ).get("area")

        builtup = pixel_area.updateMask(
            ndbi.gt(0.2)
        ).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e13,
        ).get("area")

        total = ee.Number(total)
        vegetation = ee.Number(vegetation)
        water = ee.Number(water)
        builtup = ee.Number(builtup)

        barren = total.subtract(
            vegetation
            .add(water)
            .add(builtup)
        ).max(0)

        mean_ndvi = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=10,
            maxPixels=1e13,
        ).get("NDVI")

        result = {
            "total_area_ha": total.divide(
                10000
            ).getInfo(),

            "vegetation_ha": vegetation.divide(
                10000
            ).getInfo(),

            "water_ha": water.divide(
                10000
            ).getInfo(),

            "builtup_ha": builtup.divide(
                10000
            ).getInfo(),

            "barren_ha": barren.divide(
                10000
            ).getInfo(),

            "average_ndvi": (
                ee.Number(mean_ndvi).getInfo()
                if mean_ndvi is not None
                else None
            ),
        }

        return result

    except ValueError:
        raise

    except Exception as exc:
        print(
            f"[Polygon Service] "
            f"Polygon analysis error: {exc}"
        )

        raise RuntimeError(
            f"Polygon analysis failed: {exc}"
        ) from exc
