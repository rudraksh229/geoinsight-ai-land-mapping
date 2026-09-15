import os
import json
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "xgboost_land_classifier.json"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "model",
    "label_encoder.pkl"
)

FEATURE_NAMES_PATH = os.path.join(
    BASE_DIR,
    "model",
    "feature_names.json"
)


# ============================================================
# LOAD MODEL + ENCODER + FEATURE NAMES
# ============================================================

def _get_model_and_encoder():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"XGBoost model not found: {MODEL_PATH}"
        )

    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError(
            f"Label encoder not found: {ENCODER_PATH}"
        )

    if not os.path.exists(FEATURE_NAMES_PATH):
        raise FileNotFoundError(
            f"Feature names file not found: {FEATURE_NAMES_PATH}"
        )

    # --------------------------------------------------------
    # Load XGBoost model
    # --------------------------------------------------------

    model = xgb.Booster()

    model.load_model(
        MODEL_PATH
    )

    # --------------------------------------------------------
    # Load label encoder
    # --------------------------------------------------------

    encoder = joblib.load(
        ENCODER_PATH
    )

    # --------------------------------------------------------
    # Load feature names
    # --------------------------------------------------------

    with open(
        FEATURE_NAMES_PATH,
        "r"
    ) as file:

        feature_names = json.load(
            file
        )

    if not isinstance(
        feature_names,
        list
    ):

        raise RuntimeError(
            "feature_names.json must contain a list."
        )

    if len(feature_names) != 15:

        raise RuntimeError(
            "Expected exactly 15 feature names, "
            f"but found {len(feature_names)}."
        )

    return (
        model,
        encoder,
        feature_names
    )


# ============================================================
# SINGLE LAND PREDICTION
# ============================================================

def predict_land(features):
    """
    Predict land-cover class for one location.

    Expected input:
        {
            "feature_vector": [...]
        }

    or directly:
        [...]

    Returns:
        {
            "class_id": ...,
            "class_name": ...,
            "label": ...,
            "confidence": ...
        }
    """

    (
        model,
        encoder,
        feature_names
    ) = _get_model_and_encoder()

    # --------------------------------------------------------
    # Extract feature vector
    # --------------------------------------------------------

    if isinstance(
        features,
        dict
    ):

        feature_vector = features.get(
            "feature_vector"
        )

    else:

        feature_vector = features

    if not feature_vector:

        raise ValueError(
            "Feature vector is empty."
        )

    if len(feature_vector) != 15:

        raise ValueError(
            "Expected exactly 15 features, "
            f"but received {len(feature_vector)}."
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
    # Create DataFrame
    # --------------------------------------------------------

    try:

        input_df = pd.DataFrame(
            [feature_vector],
            columns=feature_names
        )

        input_df = input_df[
            feature_names
        ]

    except Exception as exc:

        raise RuntimeError(
            "Failed to create prediction DataFrame. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # XGBoost prediction
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

    probabilities = np.asarray(
        probabilities
    )

    # --------------------------------------------------------
    # Validate prediction output
    # --------------------------------------------------------

    if probabilities.size == 0:

        raise RuntimeError(
            "XGBoost returned no prediction."
        )

    if probabilities.ndim == 1:

        class_probabilities = probabilities

    elif probabilities.ndim == 2:

        if probabilities.shape[0] != 1:

            raise RuntimeError(
                "Expected one prediction for one "
                "feature vector, but received "
                f"{probabilities.shape[0]} predictions."
            )

        class_probabilities = probabilities[0]

    else:

        raise RuntimeError(
            "Unexpected XGBoost prediction shape: "
            f"{probabilities.shape}"
        )

    # --------------------------------------------------------
    # Get predicted class
    # --------------------------------------------------------

    encoded_prediction = int(
        np.argmax(
            class_probabilities
        )
    )

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
                "Label decoding warning:",
                exc
            )

    if not class_name:

        class_name = str(
            encoded_prediction
        )

    # --------------------------------------------------------
    # Return prediction
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


# ============================================================
# GRID LAND PREDICTION
# ============================================================

def predict_land_grid(grid_features):
    """
    Predict land-cover class for multiple grid cells.

    Expected input:

        [
            {
                "grid_id": 0,
                "feature_vector": [...],
                "geometry": {...},
                "area_ha": 0.85
            },
            ...
        ]

    Returns one prediction for every valid grid cell.
    """

    (
        model,
        encoder,
        feature_names
    ) = _get_model_and_encoder()

    if not grid_features:

        raise ValueError(
            "Grid feature list is empty."
        )

    # --------------------------------------------------------
    # Prepare feature vectors
    # --------------------------------------------------------

    feature_vectors = []

    valid_cells = []

    for cell in grid_features:

        if not isinstance(
            cell,
            dict
        ):
            continue

        feature_vector = cell.get(
            "feature_vector"
        )

        if not feature_vector:
            continue

        if len(feature_vector) != 15:
            continue

        try:

            feature_vector = [
                float(value)
                for value in feature_vector
            ]

        except (
            TypeError,
            ValueError
        ):

            continue

        feature_vectors.append(
            feature_vector
        )

        valid_cells.append(
            cell
        )

    if not feature_vectors:

        raise RuntimeError(
            "No valid grid feature vectors were available "
            "for XGBoost prediction."
        )

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    try:

        input_df = pd.DataFrame(
            feature_vectors,
            columns=feature_names
        )

        input_df = input_df[
            feature_names
        ]

    except Exception as exc:

        raise RuntimeError(
            "Failed to create grid feature DataFrame. "
            f"Reason: {exc}"
        ) from exc

    # --------------------------------------------------------
    # XGBoost prediction
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
            "XGBoost grid prediction failed. "
            f"Reason: {exc}"
        ) from exc

    probabilities = np.asarray(
        probabilities
    )

    # --------------------------------------------------------
    # Validate prediction shape
    # --------------------------------------------------------

    if probabilities.size == 0:

        raise RuntimeError(
            "XGBoost returned no grid predictions."
        )

    if probabilities.ndim == 1:

        # For multiple grid cells, we expect
        # a probability vector for every cell.

        if len(valid_cells) > 1:

            raise RuntimeError(
                "XGBoost returned a 1D prediction for "
                "multiple grid cells. Expected a "
                "2D class-probability matrix."
            )

        probabilities = probabilities.reshape(
            1,
            -1
        )

    elif probabilities.ndim == 2:

        if probabilities.shape[0] != len(valid_cells):

            raise RuntimeError(
                "XGBoost prediction count does not match "
                "the number of grid cells. "
                f"Cells: {len(valid_cells)}, "
                f"Predictions: {probabilities.shape[0]}"
            )

    else:

        raise RuntimeError(
            "Unexpected XGBoost grid prediction shape: "
            f"{probabilities.shape}"
        )

    # --------------------------------------------------------
    # Build results
    # --------------------------------------------------------

    predictions = []

    for index, cell in enumerate(
        valid_cells
    ):

        class_probabilities = probabilities[
            index
        ]

        # ----------------------------------------------------
        # Predicted class
        # ----------------------------------------------------

        encoded_prediction = int(
            np.argmax(
                class_probabilities
            )
        )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        confidence = float(
            np.max(
                class_probabilities
            ) * 100
        )

        # ----------------------------------------------------
        # Decode class
        # ----------------------------------------------------

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
                    "Grid label decoding warning:",
                    exc
                )

        if not class_name:

            class_name = str(
                encoded_prediction
            )

        # ----------------------------------------------------
        # Area
        # ----------------------------------------------------

        try:

            area_ha = float(
                cell.get(
                    "area_ha",
                    0.0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            area_ha = 0.0

        # ----------------------------------------------------
        # Store prediction
        # ----------------------------------------------------

        predictions.append(
            {
                "grid_id": cell.get(
                    "grid_id",
                    index
                ),

                "geometry": cell.get(
                    "geometry"
                ),

                "area_ha": area_ha,

                "class_id": encoded_prediction,

                "class_name": class_name,

                "label": class_name,

                "confidence": round(
                    confidence,
                    2
                ),
            }
        )

    return predictions
    