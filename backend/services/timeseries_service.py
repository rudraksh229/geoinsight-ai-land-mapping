import ee

from gee_config import init_gee


# ============================================================
# VEGETATION NDVI TIME-SERIES ANALYSIS
# ============================================================

def vegetation_timeseries(
    latitude,
    longitude,
    radius,
    start_date,
    end_date,
):
    """
    Generate an NDVI time series from Sentinel-2 imagery
    for the selected region and date range.
    """

    latitude = float(latitude)
    longitude = float(longitude)
    radius = float(radius)

    start_date = str(start_date)
    end_date = str(end_date)

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not (-90 <= latitude <= 90):
        raise ValueError(
            "Invalid latitude."
        )

    if not (-180 <= longitude <= 180):
        raise ValueError(
            "Invalid longitude."
        )

    if radius <= 0:
        raise ValueError(
            "Radius must be greater than zero."
        )

    if start_date >= end_date:
        raise ValueError(
            "start_date must be earlier than end_date."
        )

    # --------------------------------------------------------
    # Initialize Earth Engine
    # --------------------------------------------------------

    try:
        init_gee()

    except Exception as exc:
        raise RuntimeError(
            "Google Earth Engine initialization failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Create region
    # --------------------------------------------------------

    point = ee.Geometry.Point(
        [
            longitude,
            latitude,
        ]
    )

    region = point.buffer(
        radius
    )

    # --------------------------------------------------------
    # Sentinel-2 collection
    # --------------------------------------------------------

    collection = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(region)
        .filterDate(
            start_date,
            end_date,
        )
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                30,
            )
        )
        .sort(
            "system:time_start"
        )
    )

    # --------------------------------------------------------
    # Check image availability
    # --------------------------------------------------------

    image_count = collection.size().getInfo()

    if image_count == 0:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius,

            "start_date": start_date,
            "end_date": end_date,

            "number_of_images": 0,

            "ndvi_timeseries": [],

            "message": (
                "No suitable Sentinel-2 imagery "
                "was found for the selected date range."
            ),
        }

    # --------------------------------------------------------
    # Calculate NDVI for every image
    #
    # Everything is kept server-side until the final
    # getInfo() call.
    # --------------------------------------------------------

    def calculate_ndvi(image):

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

        mean_ndvi = (
            ndvi
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=10,
                maxPixels=1e8,
                bestEffort=True,
            )
            .get("NDVI")
        )

        date = (
            ee.Date(
                image.get(
                    "system:time_start"
                )
            )
            .format(
                "YYYY-MM-dd"
            )
        )

        return ee.Feature(
            None,
            {
                "date": date,
                "average_ndvi": mean_ndvi,
            },
        )

    # --------------------------------------------------------
    # Map calculation over collection
    # --------------------------------------------------------

    feature_collection = (
        collection.map(
            calculate_ndvi
        )
    )

    # --------------------------------------------------------
    # Fetch complete time series in one request
    # --------------------------------------------------------

    raw_results = (
        feature_collection
        .reduceColumns(
            ee.Reducer.toList(2),
            [
                "date",
                "average_ndvi",
            ],
        )
        .get("list")
        .getInfo()
    )

    # --------------------------------------------------------
    # Format results
    # --------------------------------------------------------

    results = []

    if raw_results:

        for entry in raw_results:

            if not entry or len(entry) < 2:
                continue

            date_value = entry[0]
            ndvi_value = entry[1]

            if (
                date_value is None
                or ndvi_value is None
            ):
                continue

            try:
                results.append(
                    {
                        "date": str(
                            date_value
                        ),

                        "average_ndvi": round(
                            float(ndvi_value),
                            3,
                        ),
                    }
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    results.sort(
        key=lambda item: item["date"]
    )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,

        "start_date": start_date,
        "end_date": end_date,

        "number_of_images": len(
            results
        ),

        "ndvi_timeseries": results,

        "message": (
            "NDVI time-series analysis "
            "completed successfully."
        ),
    }
