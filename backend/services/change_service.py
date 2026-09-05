from datetime import datetime

import ee

from gee_config import init_gee


# ============================================================
# VEGETATION CHANGE DETECTION
# ============================================================

def detect_change(
    latitude,
    longitude,
    radius,
    start_date,
    end_date,
):
    """
    Detect vegetation change between two selected dates
    using Sentinel-2 NDVI.

    The service compares the best available Sentinel-2
    image near each requested date and calculates:

        NDVI(end) - NDVI(start)
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

    try:
        start_dt = datetime.strptime(
            start_date,
            "%Y-%m-%d",
        )

        end_dt = datetime.strptime(
            end_date,
            "%Y-%m-%d",
        )

    except ValueError as exc:
        raise ValueError(
            "Dates must use YYYY-MM-DD format."
        ) from exc

    if start_dt >= end_dt:
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
    # Create analysis region
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
    # Helper: get best image for a date
    # --------------------------------------------------------

    def get_image_for_date(
        target_date,
    ):
        """
        Search a short window around the requested date.

        Earth Engine filterDate() has an exclusive end date,
        so the window is explicitly extended by one day.
        """

        target_dt = datetime.strptime(
            target_date,
            "%Y-%m-%d",
        )

        window_start = (
            target_dt
        )

        window_end = (
            target_dt
        )

        # Search from requested date through the next 30 days.
        from datetime import timedelta

        window_end = (
            target_dt
            + timedelta(days=30)
        )

        start_string = (
            window_start.strftime(
                "%Y-%m-%d"
            )
        )

        end_string = (
            window_end.strftime(
                "%Y-%m-%d"
            )
        )

        image_collection = (
            ee.ImageCollection(
                "COPERNICUS/S2_SR_HARMONIZED"
            )
            .filterBounds(region)
            .filterDate(
                start_string,
                end_string,
            )
            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    30,
                )
            )
            .sort(
                "CLOUDY_PIXEL_PERCENTAGE"
            )
        )

        count = (
            image_collection
            .size()
            .getInfo()
        )

        if count == 0:
            return None

        return image_collection.first()

    # --------------------------------------------------------
    # Get start and end images
    # --------------------------------------------------------

    image1 = get_image_for_date(
        start_date
    )

    if image1 is None:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius,
            "start_date": start_date,
            "end_date": end_date,
            "average_ndvi_change": None,
            "status": "No Start-Date Imagery",
            "message": (
                "No suitable Sentinel-2 imagery "
                "was found for the start date."
            ),
        }

    image2 = get_image_for_date(
        end_date
    )

    if image2 is None:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius,
            "start_date": start_date,
            "end_date": end_date,
            "average_ndvi_change": None,
            "status": "No End-Date Imagery",
            "message": (
                "No suitable Sentinel-2 imagery "
                "was found for the end date."
            ),
        }

    # --------------------------------------------------------
    # Calculate NDVI
    # --------------------------------------------------------

    ndvi1 = (
        image1
        .normalizedDifference(
            [
                "B8",
                "B4",
            ]
        )
        .rename("NDVI")
    )

    ndvi2 = (
        image2
        .normalizedDifference(
            [
                "B8",
                "B4",
            ]
        )
        .rename("NDVI")
    )

    # --------------------------------------------------------
    # Calculate NDVI difference
    # --------------------------------------------------------

    difference = (
        ndvi2
        .subtract(
            ndvi1
        )
        .rename(
            "NDVI_CHANGE"
        )
    )

    # --------------------------------------------------------
    # Calculate mean change
    # --------------------------------------------------------

    change_result = (
        difference
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e8,
            bestEffort=True,
        )
        .getInfo()
    )

    if not change_result:
        raise RuntimeError(
            "Google Earth Engine returned empty "
            "vegetation-change statistics."
        )

    avg_change = change_result.get(
        "NDVI_CHANGE"
    )

    if avg_change is None:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius,
            "start_date": start_date,
            "end_date": end_date,
            "average_ndvi_change": None,
            "status": "No Valid NDVI Data",
            "message": (
                "NDVI could not be calculated "
                "for the selected dates."
            ),
        }

    avg_change = float(
        avg_change
    )

    # --------------------------------------------------------
    # Determine vegetation status
    # --------------------------------------------------------

    if avg_change > 0.15:
        status = (
            "Vegetation Increased"
        )

    elif avg_change < -0.15:
        status = (
            "Vegetation Decreased"
        )

    else:
        status = (
            "Minimal Change"
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

        "average_ndvi_change": round(
            avg_change,
            3,
        ),

        "status": status,

        "message": (
            "Vegetation change analysis "
            "completed successfully."
        ),
    }
