import concurrent.futures

import ee

try:
    from backend.gee_config import init_gee
except ModuleNotFoundError:
    from gee_config import init_gee


# ============================================================
# CONSTANTS
# ============================================================

GEE_TIMEOUT_SECONDS = 30

SENTINEL_COLLECTION = (
    "COPERNICUS/S2_SR_HARMONIZED"
)

SRTM_COLLECTION = (
    "USGS/SRTMGL1_003"
)

FEATURE_ORDER = [
    "Aspect",
    "B11",
    "B12",
    "B2",
    "B3",
    "B4",
    "B8",
    "BSI",
    "EVI",
    "Elevation",
    "NDBI",
    "NDVI",
    "NDWI",
    "SAVI",
    "Slope",
]


# ============================================================
# MAIN FEATURE EXTRACTION
# ============================================================

def extract_features(
    latitude,
    longitude,
    radius=500,
):
    """
    Extract the 15 features expected by the trained
    XGBoost land-classification model.

    Features:

        Aspect
        B11
        B12
        B2
        B3
        B4
        B8
        BSI
        EVI
        Elevation
        NDBI
        NDVI
        NDWI
        SAVI
        Slope

    Google Earth Engine errors are NOT replaced with fake
    satellite values. A clear RuntimeError is raised instead.
    """

    latitude = float(latitude)
    longitude = float(longitude)
    radius = float(radius)

    # --------------------------------------------------------
    # Validate coordinates
    # --------------------------------------------------------

    if not (-90 <= latitude <= 90):
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not (-180 <= longitude <= 180):
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    if radius <= 0:
        raise ValueError(
            "Radius must be greater than zero."
        )

    # --------------------------------------------------------
    # Initialize GEE
    # --------------------------------------------------------

    try:
        init_gee()
    except Exception as exc:
        raise RuntimeError(
            "Google Earth Engine initialization failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # GEE processing function
    # --------------------------------------------------------

    def run_gee():

        point = ee.Geometry.Point(
            [
                longitude,
                latitude,
            ]
        )

        roi = point.buffer(
            radius
        )

        # ----------------------------------------------------
        # Sentinel-2 collection
        # ----------------------------------------------------

        collection = (
            ee.ImageCollection(
                SENTINEL_COLLECTION
            )
            .filterBounds(roi)
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
        )

        # ----------------------------------------------------
        # Check whether imagery exists
        # ----------------------------------------------------

        image_count = collection.size().getInfo()

        if image_count == 0:
            raise RuntimeError(
                "No suitable Sentinel-2 imagery was found "
                "for the selected location and date range."
            )

        # ----------------------------------------------------
        # Median composite
        # ----------------------------------------------------

        image = collection.median()

        # ----------------------------------------------------
        # Spectral indices
        # ----------------------------------------------------

        ndvi = (
            image
            .normalizedDifference(
                [
                    "B8",
                    "B4",
                ]
            )
            .rename("NDVI")
        )

        ndwi = (
            image
            .normalizedDifference(
                [
                    "B3",
                    "B8",
                ]
            )
            .rename("NDWI")
        )

        ndbi = (
            image
            .normalizedDifference(
                [
                    "B11",
                    "B8",
                ]
            )
            .rename("NDBI")
        )

        savi = (
            image
            .expression(
                "1.5 * ((nir - red) / "
                "(nir + red + 0.5))",
                {
                    "nir": image.select("B8"),
                    "red": image.select("B4"),
                },
            )
            .rename("SAVI")
        )

        evi = (
            image
            .expression(
                "2.5 * ((nir - red) / "
                "(nir + 6 * red - "
                "7.5 * blue + 1))",
                {
                    "nir": image.select("B8"),
                    "red": image.select("B4"),
                    "blue": image.select("B2"),
                },
            )
            .rename("EVI")
        )

        bsi = (
            image
            .expression(
                "((swir + red) - "
                "(nir + blue)) / "
                "((swir + red) + "
                "(nir + blue))",
                {
                    "swir": image.select("B11"),
                    "red": image.select("B4"),
                    "nir": image.select("B8"),
                    "blue": image.select("B2"),
                },
            )
            .rename("BSI")
        )

        # ----------------------------------------------------
        # Terrain
        # ----------------------------------------------------

        terrain = ee.Terrain.products(
            ee.Image(
                SRTM_COLLECTION
            )
        )

        aspect = (
            terrain
            .select("aspect")
            .rename("Aspect")
        )

        elevation = (
            terrain
            .select("elevation")
            .rename("Elevation")
        )

        slope = (
            terrain
            .select("slope")
            .rename("Slope")
        )

        # ----------------------------------------------------
        # Feature stack
        # ----------------------------------------------------

        feature_stack = ee.Image.cat(
            [
                aspect,
                image.select("B11"),
                image.select("B12"),
                image.select("B2"),
                image.select("B3"),
                image.select("B4"),
                image.select("B8"),
                bsi,
                evi,
                elevation,
                ndbi,
                ndvi,
                ndwi,
                savi,
                slope,
            ]
        )

        # ----------------------------------------------------
        # Extract regional mean
        # ----------------------------------------------------

        values = (
            feature_stack
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=30,
                maxPixels=1e8,
                bestEffort=True,
            )
            .getInfo()
        )

        if not values:
            raise RuntimeError(
                "Google Earth Engine returned empty "
                "feature statistics."
            )

        return values

    # --------------------------------------------------------
    # Execute GEE with timeout
    # --------------------------------------------------------

    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=1
        ) as executor:

            future = executor.submit(
                run_gee
            )

            values = future.result(
                timeout=GEE_TIMEOUT_SECONDS
            )

    except concurrent.futures.TimeoutError as exc:
        raise RuntimeError(
            "Google Earth Engine analysis timed out "
            f"after {GEE_TIMEOUT_SECONDS} seconds."
        ) from exc

    except Exception as exc:
        print(
            "[GEE Feature Extraction Error]",
            str(exc),
        )

        raise RuntimeError(
            "Satellite feature extraction failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Validate every required feature
    # --------------------------------------------------------

    missing_features = []

    for feature_name in FEATURE_ORDER:
        value = values.get(
            feature_name
        )

        if value is None:
            missing_features.append(
                feature_name
            )

    if missing_features:
        raise RuntimeError(
            "Google Earth Engine did not return "
            "the following required features: "
            + ", ".join(missing_features)
        )

    # --------------------------------------------------------
    # Convert feature values to float
    # --------------------------------------------------------

    try:
        feature_vector = [
            float(values[name])
            for name in FEATURE_ORDER
        ]

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            "Google Earth Engine returned "
            "non-numeric feature values."
        ) from exc

    # --------------------------------------------------------
    # Final feature object
    # --------------------------------------------------------

    return {
        "feature_vector": feature_vector,

        "statistics": {
            "Aspect": float(
                values["Aspect"]
            ),

            "Elevation": float(
                values["Elevation"]
            ),

            "Slope": float(
                values["Slope"]
            ),

            "NDVI": float(
                values["NDVI"]
            ),

            "NDWI": float(
                values["NDWI"]
            ),

            "NDBI": float(
                values["NDBI"]
            ),

            "BSI": float(
                values["BSI"]
            ),

            "EVI": float(
                values["EVI"]
            ),

            "SAVI": float(
                values["SAVI"]
            ),
        },

        "features": {
            "B2": float(
                values["B2"]
            ),

            "B3": float(
                values["B3"]
            ),

            "B4": float(
                values["B4"]
            ),

            "B8": float(
                values["B8"]
            ),

            "B11": float(
                values["B11"]
            ),

            "B12": float(
                values["B12"]
            ),

            "BSI": float(
                values["BSI"]
            ),

            "EVI": float(
                values["EVI"]
            ),

            "SAVI": float(
                values["SAVI"]
            ),
        },
    }
