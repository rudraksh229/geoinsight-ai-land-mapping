import ee
import json
import os

# ==========================================
# SAFE EARTH ENGINE INITIALIZATION
# ==========================================

gee_key_str = os.getenv("EE_SERVICE_ACCOUNT_KEY")

if gee_key_str:
    try:
        key_dict = json.loads(gee_key_str)
        credentials = ee.ServiceAccountCredentials(
            key_dict['client_email'],
            key_data=gee_key_str
        )
        ee.Initialize(credentials, project="geoinsight-ai-503616")
        print("GEE initialized successfully via Service Account!")
    except Exception as e:
        print(f"Service Account Init Error: {e}")
else:
    print("WARNING: EE_SERVICE_ACCOUNT_KEY not found in Environment Variables!")


# ==========================================
# VEGETATION TIMESERIES FUNCTION
# ==========================================

def vegetation_health(latitude, longitude, radius, start_date, end_date):
    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(str(start_date), str(end_date))
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
        .sort("system:time_start")
    )

    def calculate_ndvi(image):
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        
        stats = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e13
        )
        
        date_str = image.date().format("YYYY-MM-dd")
        
        ndvi_val = ee.Algorithms.If(
            stats.contains("NDVI"),
            stats.get("NDVI"),
            0.0
        )
        
        return ee.Feature(None, {
            "date": date_str,
            "average_ndvi": ndvi_val
        })

    feature_collection = collection.map(calculate_ndvi)

    data = feature_collection.reduceColumns(
        ee.Reducer.toList(2), ["date", "average_ndvi"]
    ).get("list").getInfo()

    results = []
    if data:
        for entry in data:
            date, ndvi_val = entry[0], entry[1]
            if ndvi_val is not None:
                results.append({
                    "date": date,
                    "average_ndvi": round(float(ndvi_val), 3)
                })

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "number_of_images": len(results),
        "ndvi_timeseries": results
    }
    