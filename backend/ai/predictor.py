import os

import joblib
import numpy as np
import xgboost as xgb


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "xgboost_land_classifier.json",
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "label_encoder.pkl",
)


# ============================================================
# MODEL CACHE
# ============================================================

_model = None
_encoder = None


# ============================================================
# LAND-COVER CLASSES
# ============================================================

CLASS_NAMES = {
    0: "Vegetation",
    1: "Agriculture",
    2: "Built-up",
    3: "Barren",
    4: "Water",
}


# ============================================================
# LOAD MODEL
# ============================================================

def _get_model_and_encoder():
    global _model
    global _encoder

    if _model is None:

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"XGBoost model not found: {MODEL_PATH}"
            )

        print("Loading XGBoost Booster...")

        _model = xgb.Booster()

        _model.load_model(
            MODEL_PATH
        )

        print(
            "XGBoost Booster loaded successfully."
        )

    if _encoder is None:

        if not os.path.exists(ENCODER_PATH):
            raise FileNotFoundError(
                f"Label encoder not found: {ENCODER_PATH}"
            )

        _encoder = joblib.load(
            ENCODER_PATH
        )

        print(
            "Label encoder loaded successfully."
        )

        if hasattr(_encoder, "classes_"):
            print(
                "LABEL ENCODER CLASSES:",
                list(_encoder.classes_)
            )

    return _model, _encoder


# ============================================================
# PREDICTION
# ============================================================

def predict_land(features):
    """
    Predict land-cover class using the trained
    XGBoost Booster.

    Expected input:

        {
            "feature_vector": [...]
        }

    Returns confidence on a 0-100 scale.
    """

    model, encoder = _get_model_and_encoder()

    feature_vector = features.get(
        "feature_vector"
    )

    if not feature_vector:
        raise ValueError(
            "Feature vector is empty."
        )

    if len(feature_vector) != 15:
        raise ValueError(
            "Invalid feature vector length. "
            f"Expected 15 features, got {len(feature_vector)}."
        )

    # --------------------------------------------------------
    # Convert to compact float32 array
    # --------------------------------------------------------

    try:
        input_array = np.asarray(
            feature_vector,
            dtype=np.float32,
        ).reshape(1, 15)

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "Feature vector contains invalid values."
        ) from exc

    # --------------------------------------------------------
    # Create DMatrix
    # --------------------------------------------------------

    try:
        data = xgb.DMatrix(
            input_array
        )

        probabilities = model.predict(
            data
        )

    except Exception as exc:
        raise RuntimeError(
            "XGBoost prediction failed. "
            f"Reason: {exc}"
        ) from exc

    if probabilities is None:
        raise RuntimeError(
            "XGBoost returned no prediction."
        )

    probabilities = np.asarray(
        probabilities
    )

    # --------------------------------------------------------
    # Handle prediction shape
    # --------------------------------------------------------

    if probabilities.ndim == 1:

        if probabilities.size == 1:
            raise RuntimeError(
                "XGBoost model returned a single "
                "prediction instead of class probabilities."
            )

        class_probabilities = probabilities

    elif probabilities.ndim == 2:

        if probabilities.shape[0] < 1:
            raise RuntimeError(
                "XGBoost returned empty prediction output."
            )

        class_probabilities = probabilities[0]

    else:
        raise RuntimeError(
            "Unexpected XGBoost prediction output shape: "
            f"{probabilities.shape}"
        )

    # --------------------------------------------------------
    # Predicted class
    # --------------------------------------------------------

    encoded_prediction = int(
        np.argmax(
            class_probabilities
        )
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = float(
        np.max(
            class_probabilities
        ) * 100
    )

    # --------------------------------------------------------
    # Decode class
    # --------------------------------------------------------

    class_name = None

    if hasattr(
        encoder,
        "inverse_transform"
    ):
        try:

            decoded = encoder.inverse_transform(
                [encoded_prediction]
            )

            if len(decoded) > 0:
                class_name = str(
                    decoded[0]
                )

        except Exception as exc:

            print(
                f"Label encoder decoding warning: {exc}"
            )

    # --------------------------------------------------------
    # Fallback class mapping
    # --------------------------------------------------------

    if not class_name:
        class_name = CLASS_NAMES.get(
            encoded_prediction,
            "Unknown",
        )

    # --------------------------------------------------------
    # Normalize label
    # --------------------------------------------------------

    normalized_name = (
        class_name
        .strip()
        .lower()
    )

    label_map = {
        "vegetation": "Vegetation",
        "vegetative": "Vegetation",
        "agriculture": "Agriculture",
        "agricultural": "Agriculture",
        "built-up": "Built-up",
        "builtup": "Built-up",
        "urban": "Built-up",
        "barren": "Barren",
        "water": "Water",
    }

    final_class_name = label_map.get(
        normalized_name,
        class_name,
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "class_id": encoded_prediction,

        "class_name": final_class_name,

        "label": final_class_name,

        "confidence": round(
            confidence,
            2,
        ),
    }
