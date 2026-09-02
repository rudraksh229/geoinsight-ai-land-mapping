from services.landcover_service import classify_landcover


def compare_locations(location1, location2):

    first = classify_landcover(
        location1.latitude,
        location1.longitude,
        location1.radius,
    )

    second = classify_landcover(
        location2.latitude,
        location2.longitude,
        location2.radius,
    )

    comparison = {
        "location_1": first,
        "location_2": second,
        "difference": {
            "vegetation_ha":
                first["vegetation_ha"] - second["vegetation_ha"],

            "water_ha":
                first["water_ha"] - second["water_ha"],

            "builtup_ha":
                first["builtup_ha"] - second["builtup_ha"],

            "barren_ha":
                first["barren_ha"] - second["barren_ha"],
        },
    }

    return comparison
