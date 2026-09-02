import ee

# Initialize Earth Engine
ee.Initialize(project="geoinsight-ai-503616")

# Load Sentinel-2 Surface Reflectance collection
sentinel = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")

# Count total images
count = sentinel.size().getInfo()

print("Total Sentinel-2 Images:", count)
