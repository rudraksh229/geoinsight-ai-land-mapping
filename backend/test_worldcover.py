import ee

ee.Initialize(project="geoinsight-ai-503616")

# Load the first image from the collection
worldcover = ee.ImageCollection("ESA/WorldCover/v200").first()

print("Band Names:", worldcover.bandNames().getInfo())

print("\nProjection:")
print(worldcover.projection().getInfo())