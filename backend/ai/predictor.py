import os

BASE_DIR = os.path.dirname(__file__)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "xgboost_land_classifier.json"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "label_encoder.pkl"
)

# Global cached instances (Sirf pehli API request par populate honge)
_model = None
_encoder = None

CLASS_NAMES = {
    1: "Vegetation",
    2: "Agriculture",
    3: "Built-up",
    4: "Barren",
    5: "Water"
}


def _get_model_and_encoder():
    """Lazy loader: Serves cached model or loads on first call."""
    global _model, _encoder
    if _model is None or _encoder is None:
        import joblib
        from xgboost import XGBClassifier

        _model = XGBClassifier()
        _model.load_model(MODEL_PATH)
        _encoder = joblib.load(ENCODER_PATH)
        print("LABEL ENCODER CLASSES:", _encoder.classes_)

    return _model, _encoder


def predict_land(features):
    # Retrieve cached model on runtime
    model, encoder = _get_model_and_encoder()

    feature_vector = features["feature_vector"]

    # -----------------------------
    # Model prediction
    # -----------------------------
    prediction_encoded = model.predict(
        [feature_vector]
    )[0]

    prediction_encoded = int(prediction_encoded)

    # -----------------------------
    # Prediction probabilities
    # -----------------------------
    probabilities = model.predict_proba(
        [feature_vector]
    )[0]

    confidence = float(
        max(probabilities) * 100
    )

    # -----------------------------
    # IMPORTANT: XGBoost output is 0-based
    # Convert to land class ID
    # -----------------------------
    class_id = prediction_encoded + 1

    # -----------------------------
    # Get readable class name
    # -----------------------------
    class_name = CLASS_NAMES.get(
        class_id,
        "Unknown"
    )

    return {
        "class_id": class_id,
        "class_name": class_name,
        "confidence": round(confidence, 2)
    }
    