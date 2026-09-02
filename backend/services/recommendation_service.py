from schemas import RecommendationRequest


def generate_recommendation(data: RecommendationRequest):

    vegetation = data.vegetation_percent
    water = data.water_percent
    builtup = data.builtup_percent
    barren = data.barren_percent
    ndvi = data.average_ndvi

    # Mostly barren land
    if barren > 50:
        return {
            "land_type": "Mostly Barren",
            "recommendation": "Suitable for afforestation, watershed development and soil improvement.",
            "priority": "High",
            "confidence": 0.92
        }

    # Healthy vegetation
    elif vegetation > 50 and ndvi > 0.5:
        return {
            "land_type": "Healthy Vegetation",
            "recommendation": "Protect existing vegetation and promote sustainable agriculture.",
            "priority": "Medium",
            "confidence": 0.95
        }

    # Water dominant
    elif water > 30:
        return {
            "land_type": "Water Rich",
            "recommendation": "Conserve water resources and monitor seasonal water availability.",
            "priority": "Medium",
            "confidence": 0.90
        }

    # Urban area
    elif builtup > 40:
        return {
            "land_type": "Urban Area",
            "recommendation": "Promote green infrastructure and urban planning.",
            "priority": "Low",
            "confidence": 0.91
        }

    # Mixed land
    else:
        return {
            "land_type": "Mixed Land Use",
            "recommendation": "Suitable for balanced agricultural and environmental development.",
            "priority": "Medium",
            "confidence": 0.88
        }
