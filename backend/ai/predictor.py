import os
import joblib
from xgboost import XGBClassifier

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

# -----------------------------
# Load trained model
# -----------------------------

model = XGBClassifier()
model.load_model(MODEL_PATH)

# -----------------------------
# Load label encoder
# -----------------------------

encoder = joblib.load(ENCODER_PATH)

print("LABEL ENCODER CLASSES:", encoder.classes_)


# -----------------------------
# Land Classification Mapping
# -----------------------------

CLASS_NAMES = {
    1: "Vegetation",
    2: "Agriculture",
    3: "Built-up",
    4: "Barren",
    5: "Water"
}


def predict_land(features):

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
    # IMPORTANT
    # XGBoost output is 0-based
    # Convert to our land class ID
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