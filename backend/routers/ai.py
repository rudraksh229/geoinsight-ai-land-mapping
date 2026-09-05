
from fastapi import (
    APIRouter,
    HTTPException,
)

from ai.feature_extractor import extract_features
from ai.predictor import predict_land
from schemas import SatelliteRequest


router = APIRouter(
    prefix="/ai",
    tags=["AI Prediction"],
)


@router.post("/predict")
def predict(
    request: SatelliteRequest,
):
    """
    Extract satellite features and perform
    AI-based land classification.
    """

    try:
        result = extract_features(
            request.latitude,
            request.longitude,
            request.radius,
        )

        if not result:
            raise ValueError(
                "Feature extraction returned no data."
            )

        features = result.get(
            "features"
        )

        if features is None:
            raise ValueError(
                "No features were extracted from satellite imagery."
            )

        prediction = predict_land(
            result
        )

        return {
            "success": True,

            "prediction": prediction,

            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude,
                "radius": request.radius,
            },

            "statistics": result.get(
                "statistics",
                {},
            ),

            "features": features,

            "message": (
                "Prediction completed successfully."
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[AI Router] "
            f"Prediction error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "AI land prediction failed. "
                f"Reason: {str(exc)}"
            ),
        ) from exc
