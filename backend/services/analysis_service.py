from datetime import datetime
import math

from ai.feature_extractor import extract_features
from ai.predictor import predict_land


class AnalysisService:

    @staticmethod
    def analyze(latitude, longitude, radius):

        # ----------------------------------
        # Extract real Sentinel-2 features
        # ----------------------------------

        result = extract_features(
            latitude,
            longitude,
            radius
        )

        # ----------------------------------
        # AI prediction
        # ----------------------------------

        prediction = predict_land(result)

        # ----------------------------------
        # Calculate actual ROI area
        # ----------------------------------

        total_area = round(
            math.pi * (radius ** 2) / 10000,
            2
        )

        # Sentinel analysis covers the complete ROI
        mapped_area = total_area

        # ----------------------------------
        # AI confidence from XGBoost
        # ----------------------------------

        confidence = prediction.get(
            "confidence",
            0
        )

        return {

            "prediction": prediction,

            "statistics": result["statistics"],

            "features": result["features"],

            "stats": {
                "totalArea": total_area,
                "mappedArea": mapped_area,
                "confidence": confidence,
                "predictionTime": "Earth Engine + XGBoost"
            },

            "created_at": datetime.now()

        }