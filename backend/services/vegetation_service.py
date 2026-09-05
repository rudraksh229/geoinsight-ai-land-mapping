import ee

from gee_config import init_gee


# ============================================================
# VEGETATION HEALTH ANALYSIS
# ============================================================

def vegetation_health(
    latitude,
    longitude,
    radius,
    start_date,
    end_date,
):
    """
    Calculate vegetation health using Sentinel-2 NDVI
    over the requested date range.
    """

    latitude = float(latitude)
    longitude = float(longitude)
    radius = float(radius)

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

    start_date = str(start_date)
    end_date = str(end_date)

    if start_date >= end_date:
        raise ValueError(
            "start_date must be earlier than end_date."
        )

    # --------------------------------------------------------
    # Initialize Earth Engine
    # --------------------------------------------------------

    init_gee()

    # --------------------------------------------------------
    # Region
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
    # Check imagery availability
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
    # Calculate NDVI for each image
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

        stats = (
            ndvi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=10,
                maxPixels=1e8,
                bestEffort=True,
            )
        )

        ndvi_value = ee.Algorithms.If(
            stats.contains("NDVI"),
            stats.get("NDVI"),
            None,
        )

        date_value = (
            image
            .date()
            .format("YYYY-MM-dd")
        )

        return ee.Feature(
            None,
            {
                "date": date_value,
                "average_ndvi": ndvi_value,
            },
        )

    feature_collection = (
        collection.map(
            calculate_ndvi
        )
    )

    # --------------------------------------------------------
    # Fetch all results in ONE server request
    # --------------------------------------------------------

    result = (
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
    # Format response
    # --------------------------------------------------------

    ndvi_timeseries = []

    if result:
        for entry in result:

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
                ndvi_timeseries.append(
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

    ndvi_timeseries.sort(
        key=lambda item: item["date"]
    )

    # --------------------------------------------------------
    # Basic health summary
    # --------------------------------------------------------

    ndvi_values = [
        item["average_ndvi"]
        for item in ndvi_timeseries
    ]

    if ndvi_values:

        average_ndvi = round(
            sum(ndvi_values)
            / len(ndvi_values),
            3,
        )

        minimum_ndvi = round(
            min(ndvi_values),
            3,
        )

        maximum_ndvi = round(
            max(ndvi_values),
            3,
        )

        if average_ndvi >= 0.6:
            health_status = "Healthy"

        elif average_ndvi >= 0.4:
            health_status = "Moderate"

        elif average_ndvi >= 0.2:
            health_status = "Low"

        else:
            health_status = "Very Low"

    else:
        average_ndvi = None
        minimum_ndvi = None
        maximum_ndvi = None
        health_status = "No Data"

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
            ndvi_timeseries
        ),

        "average_ndvi": average_ndvi,

        "minimum_ndvi": minimum_ndvi,

        "maximum_ndvi": maximum_ndvi,

        "health_status": health_status,

        "ndvi_timeseries": ndvi_timeseries,

        "message": (
            "Vegetation health analysis "
            "completed successfully."
        ),
    }
