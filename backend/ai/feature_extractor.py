import ee
import math
try:
    from backend.gee_config import init_gee
except ModuleNotFoundError:
    from gee_config import init_gee


# ============================================================
# CONSTANTS
# ============================================================

SENTINEL_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
SRTM_COLLECTION = "USGS/SRTMGL1_003"

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

    The feature order is kept exactly the same as the
    trained model.

    GEE processing is optimized for Render by:
        - avoiding a full-year median composite
        - selecting the least-cloudy image directly
        - performing one reduceRegion operation
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
    # Initialize Google Earth Engine
    # --------------------------------------------------------

    try:
        init_gee()
    except Exception as exc:
        raise RuntimeError(
            "Google Earth Engine initialization failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Geometry
    # --------------------------------------------------------

    point = ee.Geometry.Point(
        [
            longitude,
            latitude,
        ]
    )

    roi = point.buffer(radius)

    # --------------------------------------------------------
    # Sentinel-2 collection
    # --------------------------------------------------------

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
        .sort(
            "CLOUDY_PIXEL_PERCENTAGE"
        )
    )

    # --------------------------------------------------------
    # Select least-cloudy image
    # --------------------------------------------------------

    image = collection.first()

    # --------------------------------------------------------
    # Verify image exists
    # --------------------------------------------------------

    try:
        image_info = image.getInfo()
    except Exception as exc:
        raise RuntimeError(
            "Unable to retrieve Sentinel-2 imagery from "
            f"Google Earth Engine. Reason: {exc}"
        ) from exc

    if not image_info:
        raise RuntimeError(
            "No suitable Sentinel-2 imagery was found "
            "for the selected location and date range."
        )

    # --------------------------------------------------------
    # Spectral indices
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Terrain
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Feature stack
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Extract regional mean
    # --------------------------------------------------------

    try:
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

    except Exception as exc:
        raise RuntimeError(
            "Google Earth Engine failed while calculating "
            f"satellite features. Reason: {exc}"
        ) from exc

    if not values:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "feature statistics."
        )

    # --------------------------------------------------------
    # Validate required features
    # --------------------------------------------------------

    missing_features = [
        feature_name
        for feature_name in FEATURE_ORDER
        if values.get(feature_name) is None
    ]

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
            "Aspect": float(values["Aspect"]),
            "Elevation": float(values["Elevation"]),
            "Slope": float(values["Slope"]),
            "NDVI": float(values["NDVI"]),
            "NDWI": float(values["NDWI"]),
            "NDBI": float(values["NDBI"]),
            "BSI": float(values["BSI"]),
            "EVI": float(values["EVI"]),
            "SAVI": float(values["SAVI"]),
        },

        "features": {
            "B2": float(values["B2"]),
            "B3": float(values["B3"]),
            "B4": float(values["B4"]),
            "B8": float(values["B8"]),
            "B11": float(values["B11"]),
            "B12": float(values["B12"]),
            "BSI": float(values["BSI"]),
            "EVI": float(values["EVI"]),
            "SAVI": float(values["SAVI"]),
        },
    }
# ============================================================
# GRID FEATURE EXTRACTION FOR MULTI-CLASS MAP
# ============================================================
# ============================================================
# GRID FEATURE EXTRACTION FOR MULTI-CLASS MAP
# ============================================================

def extract_feature_grid(
    latitude,
    longitude,
    radius=500,
    grid_size=100,
):
    """
    Extract feature values for multiple grid cells inside
    the selected ROI.

    Each grid cell contains the same 15 features expected
    by the trained XGBoost model.
    """

    latitude = float(latitude)
    longitude = float(longitude)
    radius = float(radius)
    grid_size = int(grid_size)

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

    if grid_size <= 0:
        raise ValueError(
            "Grid size must be greater than zero."
        )

    # --------------------------------------------------------
    # Initialize Google Earth Engine
    # --------------------------------------------------------

    try:
        init_gee()
    except Exception as exc:
        raise RuntimeError(
            "Google Earth Engine initialization failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Geometry
    # --------------------------------------------------------

    point = ee.Geometry.Point(
        [
            longitude,
            latitude,
        ]
    )

    roi = point.buffer(radius)

    # --------------------------------------------------------
    # Sentinel-2 collection
    # --------------------------------------------------------

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
        .sort(
            "CLOUDY_PIXEL_PERCENTAGE"
        )
    )

    # --------------------------------------------------------
    # Select least-cloudy image
    # --------------------------------------------------------

    image = collection.first()

    try:
        image_info = image.getInfo()
    except Exception as exc:
        raise RuntimeError(
            "Unable to retrieve Sentinel-2 imagery. "
            f"Reason: {exc}"
        ) from exc

    if not image_info:
        raise RuntimeError(
            "No suitable Sentinel-2 imagery was found."
        )

    # --------------------------------------------------------
    # Spectral indices
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Terrain
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Feature stack
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create regular grid
    # --------------------------------------------------------

    earth_radius = 6378137.0

    lat_rad = (
        latitude
        * math.pi
        / 180.0
    )

    # Convert metres to approximate degrees.
    lat_step = (
        grid_size
        / earth_radius
        * 180.0
        / math.pi
    )

    cos_lat = max(
        0.01,
        abs(
            math.cos(lat_rad)
        ),
    )

    lng_step = (
        grid_size
        / (
            earth_radius
            * cos_lat
        )
        * 180.0
        / math.pi
    )

    # --------------------------------------------------------
    # ROI bounding box
    # --------------------------------------------------------

    lat_radius = (
        radius
        / earth_radius
        * 180.0
        / math.pi
    )

    lng_radius = (
        radius
        / (
            earth_radius
            * cos_lat
        )
        * 180.0
        / math.pi
    )

    lat_min = latitude - lat_radius
    lat_max = latitude + lat_radius

    lng_min = longitude - lng_radius
    lng_max = longitude + lng_radius

    # --------------------------------------------------------
    # Build grid FeatureCollection
    # --------------------------------------------------------

    grid_features_ee = []

    grid_id = 0

    current_lat = lat_min

    while current_lat < lat_max:

        current_lng = lng_min

        while current_lng < lng_max:

            next_lat = min(
                current_lat + lat_step,
                lat_max,
            )

            next_lng = min(
                current_lng + lng_step,
                lng_max,
            )

            cell = ee.Geometry.Rectangle(
                [
                    current_lng,
                    current_lat,
                    next_lng,
                    next_lat,
                ],
                geodesic=True,
            )

            # Keep only the part of the cell
            # that lies inside the circular ROI.
            clipped_cell = cell.intersection(
                roi,
                maxError=1,
            )

            area_ha = (
                clipped_cell
                .area(
                    maxError=1
                )
                .divide(10000)
            )

            grid_features_ee.append(
                ee.Feature(
                    clipped_cell,
                    {
                        "grid_id": grid_id,
                        "area_ha": area_ha,
                    },
                )
            )

            grid_id += 1

            current_lng += lng_step

        current_lat += lat_step

    if not grid_features_ee:
        raise RuntimeError(
            "No grid cells were created."
        )

    grid = ee.FeatureCollection(
        grid_features_ee
    )

    # --------------------------------------------------------
    # Extract mean features for every grid cell
    # --------------------------------------------------------

    try:

        sampled = (
            feature_stack
            .reduceRegions(
                collection=grid,
                reducer=ee.Reducer.mean(),
                scale=30,
                tileScale=4,
            )
            .getInfo()
        )

    except Exception as exc:

        raise RuntimeError(
            "Google Earth Engine failed while extracting "
            f"grid features. Reason: {exc}"
        ) from exc

    if not sampled or "features" not in sampled:

        raise RuntimeError(
            "Google Earth Engine returned no grid features."
        )

    # --------------------------------------------------------
    # Convert GEE output
    # --------------------------------------------------------

    grid_features = []

    for index, feature in enumerate(
        sampled["features"]
    ):

        properties = feature.get(
            "properties",
            {},
        )

        values = []

        valid = True

        # ----------------------------------------------------
        # Validate all 15 features
        # ----------------------------------------------------

        for feature_name in FEATURE_ORDER:

            value = properties.get(
                feature_name
            )

            if value is None:
                valid = False
                break

            try:

                values.append(
                    float(value)
                )

            except (
                TypeError,
                ValueError,
            ):

                valid = False
                break

        if not valid:
            continue

        # ----------------------------------------------------
        # Area
        # ----------------------------------------------------

        try:

            area_ha = float(
                properties.get(
                    "area_ha",
                    0.0,
                )
                or 0.0
            )

        except (
            TypeError,
            ValueError,
        ):

            area_ha = 0.0

        # ----------------------------------------------------
        # Store grid cell
        # ----------------------------------------------------

        grid_features.append(
            {
                "grid_id": properties.get(
                    "grid_id",
                    index,
                ),

                "feature_vector": values,

                "geometry": feature.get(
                    "geometry"
                ),

                "area_ha": area_ha,
            }
        )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    if not grid_features:

        raise RuntimeError(
            "No valid grid cells with complete "
            "15-feature vectors were generated."
        )

    return grid_features