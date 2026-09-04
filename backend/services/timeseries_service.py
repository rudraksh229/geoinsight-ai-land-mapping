import ee
import json
import os

# ==========================================
# EARTH ENGINE INITIALIZATION FUNCTION
# ==========================================

def init_earth_engine():
    """Module load time par crash hone se bachane ke liye EE initialization ko handle karein"""
    gee_key_str = os.getenv("EE_SERVICE_ACCOUNT_KEY")
    project_id = os.getenv("GEE_PROJECT_ID", "geoinsight-ai-503616")

    if gee_key_str:
        try:
            key_dict = json.loads(gee_key_str)
            credentials = ee.ServiceAccountCredentials(
                key_dict['client_email'],
                key_data=gee_key_str
            )
            ee.Initialize(credentials, project=project_id)
            print("GEE initialized successfully via Service Account!")
            return True
        except Exception as e:
            print(f"Service Account Init Error: {e}")

    try:
        ee.Initialize(project=project_id)
        print("GEE initialized via Default Credentials!")
        return True
    except Exception as fallback_err:
        print(f"Fallback Init Failed: {fallback_err}")
        return False


# File load hone par safely initialize karein
init_earth_engine()


# ==========================================
# VEGETATION TIMESERIES FUNCTION
# ==========================================

def vegetation_health(latitude, longitude, radius, start_date, end_date):
    # Safety Check: Guarantee Initialization
    if not ee.data._credentials:
        initialized = init_earth_engine()
        if not initialized:
            raise RuntimeError("Earth Engine API initialize nahi ho sakti. Check environment credentials.")

    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(radius)

    # Sentinel-2 Collection
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(str(start_date), str(end_date))
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
        .sort("system:time_start")
    )

    # Fast Vectorized Function
    def calculate_ndvi(image):
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        
        stats = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e13
        )
        
        date_str = image.date().format("YYYY-MM-dd")
        
        # Server-side Null check
        ndvi_val = ee.Algorithms.If(
            stats.contains("NDVI"),
            stats.get("NDVI"),
            0.0
        )
        
        return ee.Feature(None, {
            "date": date_str,
            "average_ndvi": ndvi_val
        })

    # Processing in single network request
    feature_collection = collection.map(calculate_ndvi)

    data = feature_collection.reduceColumns(
        ee.Reducer.toList(2), ["date", "average_ndvi"]
    ).get("list").getInfo()

    # Format JSON safely
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
    