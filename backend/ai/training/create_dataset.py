import ee

# ----------------------------------------------------
# Initialize Earth Engine
# ----------------------------------------------------

ee.Initialize(project="geoinsight-ai-503616")

# ----------------------------------------------------
# Study Area
# ----------------------------------------------------

sehore = ee.Geometry.Rectangle([
    76.20,
    22.90,
    78.10,
    23.90
])

# ----------------------------------------------------
# Cloud Mask using QA60
# ----------------------------------------------------

def mask_s2_clouds(image):

    qa = image.select("QA60")

    cloud = 1 << 10
    cirrus = 1 << 11

    mask = (
        qa.bitwiseAnd(cloud).eq(0)
        .And(qa.bitwiseAnd(cirrus).eq(0))
    )

    return (
        image
        .updateMask(mask)
        .divide(10000)
        .copyProperties(image, image.propertyNames())
    )

# ----------------------------------------------------
# Safe Seasonal Composite
# ----------------------------------------------------

def seasonal_composite(start, end):

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(sehore)
        .filterDate(start, end)
        .map(mask_s2_clouds)
    )

    count = collection.size()

    return ee.Image(
        ee.Algorithms.If(
            count.gt(0),
            collection.median(),
            annual_image
        )
    )

# ----------------------------------------------------
# Annual Composite
# ----------------------------------------------------

annual_image = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(sehore)
    .filterDate("2024-01-01", "2024-12-31")
    .map(mask_s2_clouds)
    .median()
)

# ----------------------------------------------------
# Seasonal Images
# ----------------------------------------------------

winter = seasonal_composite(
    "2024-01-01",
    "2024-03-31"
)

summer = seasonal_composite(
    "2024-04-01",
    "2024-06-30"
)

monsoon = seasonal_composite(
    "2024-07-01",
    "2024-09-30"
)

# ----------------------------------------------------
# Rename Bands
# ----------------------------------------------------

winter = winter.select(
    ["B2","B3","B4","B8","B11","B12"],
    ["W_B2","W_B3","W_B4","W_B8","W_B11","W_B12"]
)

summer = summer.select(
    ["B2","B3","B4","B8","B11","B12"],
    ["S_B2","S_B3","S_B4","S_B8","S_B11","S_B12"]
)

monsoon = monsoon.select(
    ["B2","B3","B4","B8","B11","B12"],
    ["M_B2","M_B3","M_B4","M_B8","M_B11","M_B12"]
)

# ----------------------------------------------------
# Annual Indices
# ----------------------------------------------------

ndvi = annual_image.normalizedDifference(
    ["B8","B4"]
).rename("NDVI")

ndwi = annual_image.normalizedDifference(
    ["B3","B8"]
).rename("NDWI")

ndbi = annual_image.normalizedDifference(
    ["B11","B8"]
).rename("NDBI")

savi = annual_image.expression(
    "1.5*((nir-red)/(nir+red+0.5))",
    {
        "nir": annual_image.select("B8"),
        "red": annual_image.select("B4")
    }
).rename("SAVI")

evi = annual_image.expression(
    "2.5*((nir-red)/(nir+6*red-7.5*blue+1))",
    {
        "nir": annual_image.select("B8"),
        "red": annual_image.select("B4"),
        "blue": annual_image.select("B2")
    }
).rename("EVI")

bsi = annual_image.expression(
    "((swir+red)-(nir+blue))/((swir+red)+(nir+blue))",
    {
        "swir": annual_image.select("B11"),
        "red": annual_image.select("B4"),
        "nir": annual_image.select("B8"),
        "blue": annual_image.select("B2")
    }
).rename("BSI")

# ----------------------------------------------------
# Terrain
# ----------------------------------------------------

terrain = ee.Terrain.products(
    ee.Image("USGS/SRTMGL1_003")
)

elevation = terrain.select("elevation").rename("Elevation")

slope = terrain.select("slope").rename("Slope")

aspect = terrain.select("aspect").rename("Aspect")

# ----------------------------------------------------
# WorldCover
# ----------------------------------------------------

label = (
    ee.ImageCollection("ESA/WorldCover/v200")
    .first()
    .select("Map")
    .rename("label")
)

# ----------------------------------------------------
# Feature Stack
# ----------------------------------------------------

stack = (
    winter
    .addBands(summer)
    .addBands(monsoon)
    .addBands(ndvi)
    .addBands(ndwi)
    .addBands(ndbi)
    .addBands(savi)
    .addBands(evi)
    .addBands(bsi)
    .addBands(elevation)
    .addBands(slope)
    .addBands(aspect)
    .addBands(label)
)

# ----------------------------------------------------
# Stratified Sampling
# ----------------------------------------------------

samples = stack.stratifiedSample(
    numPoints=8000,
    classBand="label",
    region=sehore,
    scale=10,
    seed=42,
    geometries=False
)

# ----------------------------------------------------
# Export
# ----------------------------------------------------

task = ee.batch.Export.table.toDrive(
    collection=samples,
    description="Sehore_Dataset_Final",
    fileNamePrefix="Sehore_Dataset_Final",
    fileFormat="CSV"
)

task.start()

print("Export Started Successfully")
print("Check the Tasks tab in Earth Engine:")
print("https://code.earthengine.google.com/tasks")
print("CSV will appear in your Google Drive after completion.")