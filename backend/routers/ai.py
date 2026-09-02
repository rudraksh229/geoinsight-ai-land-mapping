from fastapi import APIRouter

from ai.feature_extractor import extract_features
from ai.predictor import predict_land
from schemas import SatelliteRequest

router = APIRouter(
    prefix="/ai",
    tags=["AI Prediction"]
)


@router.post("/predict")
def predict(request: SatelliteRequest):

    result = extract_features(
        request.latitude,
        request.longitude,
        request.radius
    )

    prediction = predict_land(result)

    return {
        "success": True,
        "prediction": prediction,
        "location": {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "radius": request.radius
        },
        "statistics": result["statistics"],
        "features": result["features"],
        "message": "Prediction completed successfully."
    }
