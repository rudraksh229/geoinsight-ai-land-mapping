import math
import time
from datetime import datetime

try:
    from backend.ai.feature_extractor import extract_features
    from backend.ai.predictor import predict_land
except ModuleNotFoundError:
    from ai.feature_extractor import extract_features
    from ai.predictor import predict_land


class AnalysisService:

    @staticmethod
    def analyze(latitude, longitude, radius):
        """
        Complete AI analysis pipeline:

        Location
            ↓
        Google Earth Engine
            ↓
        Sentinel-2 feature extraction
            ↓
        XGBoost prediction
            ↓
        Analysis result
        """

        start_time = time.time()

        latitude = float(latitude)
        longitude = float(longitude)
        radius = float(radius)

        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid latitude.")

        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid longitude.")

        if radius <= 0:
            raise ValueError(
                "Radius must be greater than zero."
            )

        # --------------------------------------------------
        # 1. EXTRACT REAL SATELLITE FEATURES
        # --------------------------------------------------

        result = extract_features(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        if not result:
            raise RuntimeError(
                "Google Earth Engine returned no feature data."
            )

        feature_vector = result.get(
            "feature_vector"
        )

        if not feature_vector:
            raise RuntimeError(
                "Feature extraction returned an empty feature vector."
            )

        # Make sure all features are numeric.
        try:
            feature_vector = [
                float(value)
                for value in feature_vector
            ]
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "Invalid feature values returned by Google Earth Engine."
            ) from exc

        # The trained model expects 15 features.
        if len(feature_vector) != 15:
            raise RuntimeError(
                "Invalid feature vector length. "
                f"Expected 15 features, got {len(feature_vector)}."
            )

        # --------------------------------------------------
        # 2. RUN XGBOOST PREDICTION
        # --------------------------------------------------

        prediction = predict_land(result)

        if not prediction:
            raise RuntimeError(
                "XGBoost prediction returned no result."
            )

        # --------------------------------------------------
        # 3. NORMALIZE PREDICTION DATA
        # --------------------------------------------------

        confidence = float(
            prediction.get(
                "confidence",
                0.0,
            )
        )

        # Predictor normally returns confidence as 0-100.
        # Keep this service internally consistent.
        if 0 <= confidence <= 1:
            confidence_percent = confidence * 100
        else:
            confidence_percent = confidence

        confidence_percent = max(
            0.0,
            min(
                100.0,
                confidence_percent,
            ),
        )

        class_id = prediction.get(
            "class_id"
        )

        class_name = (
            prediction.get("class_name")
            or prediction.get("label")
            or "Unknown"
        )

        normalized_prediction = {
            "class_id": (
                int(class_id)
                if class_id is not None
                else None
            ),
            "class_name": str(class_name),
            "label": str(class_name),
            "confidence": round(
                confidence_percent,
                2,
            ),
        }

        # --------------------------------------------------
        # 4. AREA CALCULATION
        # --------------------------------------------------

        # radius is in metres.
        #
        # Area of circle:
        # π × r²
        #
        # Convert square metres → hectares:
        # 1 hectare = 10,000 m²

        total_area = (
            math.pi * (radius ** 2)
        ) / 10000

        total_area = round(
            total_area,
            2,
        )

        mapped_area = total_area

        # --------------------------------------------------
        # 5. PERFORMANCE
        # --------------------------------------------------

        prediction_time = round(
            time.time() - start_time,
            2,
        )

        # --------------------------------------------------
        # 6. FINAL RESULT
        # --------------------------------------------------

        return {
            "prediction": normalized_prediction,

            "statistics": result.get(
                "statistics",
                {},
            ),

            "features": result.get(
                "features",
                {},
            ),

            "feature_vector": feature_vector,

            "stats": {
                "totalArea": total_area,
                "mappedArea": mapped_area,
                "confidence": round(
                    confidence_percent,
                    2,
                ),
                "predictionTime": (
                    f"{prediction_time}s"
                ),
            },

            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
            },

            "created_at": datetime.utcnow(),
        }
