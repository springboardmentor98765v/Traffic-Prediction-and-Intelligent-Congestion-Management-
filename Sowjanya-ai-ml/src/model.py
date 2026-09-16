from pathlib import Path

import joblib
import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "congestion_model.pkl"


# Load trained Random Forest model
model = joblib.load(MODEL_PATH)


def predict_congestion_ml(
    road_id_encoded,
    vehicle_count,
    avg_speed,
    density,
    hour,
    day_of_week
):
    """
    Predict congestion level using the trained Random Forest model.
    """

    # Peak-hour feature
    is_peak_hour = int(
        ((7 <= hour <= 10) or (17 <= hour <= 20))
    )

    # Feature order MUST match training notebook
    input_data = pd.DataFrame([{
        "road_id_encoded": road_id_encoded,
        "vehicle_count": vehicle_count,
        "avg_speed": avg_speed,
        "density": density,
        "hour": hour,
        "day_of_week": day_of_week,
        "is_peak_hour": is_peak_hour
    }])

    # Prediction
    prediction = model.predict(input_data)[0]

    # Confidence
    probabilities = model.predict_proba(input_data)[0]
    confidence = float(max(probabilities))

    return {
        "prediction": str(prediction),
        "confidence": round(confidence, 4),
        "model_version": "random-forest-v1"
    }
