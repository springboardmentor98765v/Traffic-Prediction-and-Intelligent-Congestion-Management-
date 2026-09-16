from pathlib import Path
import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "congestion_model.pkl"

model = joblib.load(MODEL_PATH)


def predict_congestion_ml(
    road_id_encoded,
    vehicle_count,
    avg_speed,
    density,
    hour,
    day_of_week
):
    is_peak_hour = 1 if (7 <= hour <= 10 or 17 <= hour <= 20) else 0

    data = pd.DataFrame([{
        "road_id_encoded": road_id_encoded,
        "vehicle_count": vehicle_count,
        "avg_speed": avg_speed,
        "density": density,
        "hour": hour,
        "day_of_week": day_of_week,
        "is_peak_hour": is_peak_hour
    }])

    prediction = model.predict(data)[0]

    confidence = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(data)[0]
        confidence = float(max(probabilities))

    return str(prediction), confidence