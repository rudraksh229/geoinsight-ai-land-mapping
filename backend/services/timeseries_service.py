import ee
from gee_config import init_gee


def vegetation_timeseries(latitude, longitude, radius, start_date, end_date):
    # Safe lazy initialization on execution
    init_gee()

    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(str(start_date), str(end_date))
        .sort("system:time_start")
    )

    images = collection.toList(collection.size())

    size = images.size().getInfo()

    results = []

    for i in range(size):

        image = ee.Image(images.get(i))

        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

        mean_ndvi = (
            ndvi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=10,
                maxPixels=1e13,
            )
            .get("NDVI")
        )

        date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd")

        results.append(
            {
                "date": date.getInfo(),
                "average_ndvi": round(ee.Number(mean_ndvi).getInfo(), 3),
            }
        )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "number_of_images": size,
        "ndvi_timeseries": results,
    }
    