import os
import json

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_land_classifier.json"
)

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "label_encoder.pkl"
)

FEATURES_PATH = os.path.join(
    MODEL_DIR,
    "feature_names.json"
)


# ============================================================
# MODEL CACHE
# ============================================================

_model = None
_encoder = None
_feature_names = None


# ============================================================
# LOAD MODEL, ENCODER AND FEATURES
# ============================================================

def _get_model_and_encoder():

    global _model
    global _encoder
    global _feature_names

    # --------------------------------------------------------
    # Load XGBoost model
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Load label encoder
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Load feature names
    # --------------------------------------------------------

    if _feature_names is None:

        if not os.path.exists(FEATURES_PATH):
            raise FileNotFoundError(
                f"Feature names file not found: {FEATURES_PATH}"
            )

        with open(
            FEATURES_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            _feature_names = json.load(file)

        if not isinstance(
            _feature_names,
            list
        ):

            raise ValueError(
                "feature_names.json must contain a list."
            )

        if len(_feature_names) != 15:

            raise ValueError(
                "Invalid feature_names.json. "
                f"Expected 15 features, got {len(_feature_names)}."
            )

        print(
            "FEATURE NAMES:",
            _feature_names
        )

    return (
        _model,
        _encoder,
        _feature_names
    )


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

    The feature vector is converted into a Pandas
    DataFrame with the exact feature names used
    during model training.
    """

    (
        model,
        encoder,
        feature_names
    ) = _get_model_and_encoder()

    # --------------------------------------------------------
    # Get feature vector
    # --------------------------------------------------------

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
    # Convert values to float
    # --------------------------------------------------------

    try:

        feature_vector = [
            float(value)
            for value in feature_vector
        ]

    except (
        TypeError,
        ValueError
    ) as exc:

        raise ValueError(
            "Feature vector contains invalid values."
        ) from exc

    # --------------------------------------------------------
    # Create named DataFrame
    # --------------------------------------------------------

    try:

        input_df = pd.DataFrame(
            [
                feature_vector
            ],
            columns=feature_names
        )

    except Exception as exc:

        raise RuntimeError(
            "Failed to create feature DataFrame. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Ensure exact feature order
    # --------------------------------------------------------

    input_df = input_df[
        feature_names
    ]

    # --------------------------------------------------------
    # Create DMatrix WITH feature names
    # --------------------------------------------------------

    try:

        data = xgb.DMatrix(
            input_df,
            feature_names=feature_names
        )

        probabilities = model.predict(
            data
        )

    except Exception as exc:

        raise RuntimeError(
            "XGBoost prediction failed. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Validate prediction output
    # --------------------------------------------------------

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
    # Predicted encoded class
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
    # Decode class using LabelEncoder
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
                "Label encoder decoding warning:",
                exc
            )

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not class_name:

        class_name = str(
            encoded_prediction
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "class_id": encoded_prediction,

        "class_name": class_name,

        "label": class_name,

        "confidence": round(
            confidence,
            2
        ),
    }
