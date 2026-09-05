from services.landcover_service import classify_landcover


# ============================================================
# LOCATION COMPARISON
# ============================================================

def compare_locations(
    location1,
    location2,
):
    """
    Compare land-cover statistics between two locations.

    Both locations are analyzed using the same
    Sentinel-2 land-cover service.
    """

    # --------------------------------------------------------
    # Analyze first location
    # --------------------------------------------------------

    first = classify_landcover(
        latitude=location1.latitude,
        longitude=location1.longitude,
        radius=location1.radius,
    )

    # --------------------------------------------------------
    # Analyze second location
    # --------------------------------------------------------

    second = classify_landcover(
        latitude=location2.latitude,
        longitude=location2.longitude,
        radius=location2.radius,
    )

    # --------------------------------------------------------
    # Extract land-cover values safely
    # --------------------------------------------------------

    first_land_cover = first.get(
        "land_cover",
        {},
    )

    second_land_cover = second.get(
        "land_cover",
        {},
    )

    first_vegetation = float(
        first_land_cover.get(
            "vegetation",
            0.0,
        )
        or 0.0
    )

    second_vegetation = float(
        second_land_cover.get(
            "vegetation",
            0.0,
        )
        or 0.0
    )

    first_water = float(
        first_land_cover.get(
            "water",
            0.0,
        )
        or 0.0
    )

    second_water = float(
        second_land_cover.get(
            "water",
            0.0,
        )
        or 0.0
    )

    first_builtup = float(
        first_land_cover.get(
            "builtup",
            0.0,
        )
        or 0.0
    )

    second_builtup = float(
        second_land_cover.get(
            "builtup",
            0.0,
        )
        or 0.0
    )

    first_barren = float(
        first_land_cover.get(
            "barren",
            0.0,
        )
        or 0.0
    )

    second_barren = float(
        second_land_cover.get(
            "barren",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # Calculate differences
    #
    # Positive = Location 1 has more
    # Negative = Location 2 has more
    # --------------------------------------------------------

    vegetation_difference = (
        first_vegetation
        - second_vegetation
    )

    water_difference = (
        first_water
        - second_water
    )

    builtup_difference = (
        first_builtup
        - second_builtup
    )

    barren_difference = (
        first_barren
        - second_barren
    )

    # --------------------------------------------------------
    # Final comparison response
    # --------------------------------------------------------

    return {
        "location_1": first,

        "location_2": second,

        "difference": {
            "vegetation_ha": round(
                vegetation_difference,
                2,
            ),

            "water_ha": round(
                water_difference,
                2,
            ),

            "builtup_ha": round(
                builtup_difference,
                2,
            ),

            "barren_ha": round(
                barren_difference,
                2,
            ),
        },
    }
