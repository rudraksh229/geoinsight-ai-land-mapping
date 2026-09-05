from schemas import RecommendationRequest


# ============================================================
# LAND-USE RECOMMENDATION
# ============================================================

def generate_recommendation(
    data: RecommendationRequest,
):
    """
    Generate a land-use recommendation based on
    land-cover percentages and average NDVI.

    This is a rule-based recommendation system.
    It does not replace the XGBoost land-classification model.
    """

    # --------------------------------------------------------
    # Read and validate values
    # --------------------------------------------------------

    vegetation = float(
        data.vegetation_percent
    )

    water = float(
        data.water_percent
    )

    builtup = float(
        data.builtup_percent
    )

    barren = float(
        data.barren_percent
    )

    ndvi = float(
        data.average_ndvi
    )

    # --------------------------------------------------------
    # Keep percentages within valid range
    # --------------------------------------------------------

    vegetation = max(
        0.0,
        min(100.0, vegetation),
    )

    water = max(
        0.0,
        min(100.0, water),
    )

    builtup = max(
        0.0,
        min(100.0, builtup),
    )

    barren = max(
        0.0,
        min(100.0, barren),
    )

    # NDVI normally ranges approximately from -1 to 1.
    ndvi = max(
        -1.0,
        min(1.0, ndvi),
    )

    # --------------------------------------------------------
    # Recommendation rules
    # --------------------------------------------------------

    # Mostly barren land
    if barren > 50:
        return {
            "land_type": "Mostly Barren",

            "recommendation": (
                "Suitable for afforestation, "
                "watershed development and "
                "soil improvement."
            ),

            "priority": "High",

            "confidence": 0.92,
        }

    # Healthy vegetation
    elif (
        vegetation > 50
        and ndvi > 0.5
    ):
        return {
            "land_type": "Healthy Vegetation",

            "recommendation": (
                "Protect existing vegetation "
                "and promote sustainable "
                "agriculture."
            ),

            "priority": "Medium",

            "confidence": 0.95,
        }

    # Water dominant
    elif water > 30:
        return {
            "land_type": "Water Rich",

            "recommendation": (
                "Conserve water resources "
                "and monitor seasonal "
                "water availability."
            ),

            "priority": "Medium",

            "confidence": 0.90,
        }

    # Urban / built-up dominant
    elif builtup > 40:
        return {
            "land_type": "Urban Area",

            "recommendation": (
                "Promote green infrastructure "
                "and responsible urban planning."
            ),

            "priority": "Low",

            "confidence": 0.91,
        }

    # Mixed land use
    else:
        return {
            "land_type": "Mixed Land Use",

            "recommendation": (
                "Suitable for balanced "
                "agricultural and environmental "
                "development."
            ),

            "priority": "Medium",

            "confidence": 0.88,
        }
