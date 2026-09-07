from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.traffic.service import get_latest_traffic


MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "Manasa-Maskan_AI-ML-Intelligent-Routing"
    / "src"
    / "traffic_model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_congestion(
    db: Session,
    road_id: int,
):
    traffic = get_latest_traffic(
        db,
        road_id,
    )

    if not traffic:
        return None

    recorded_at = traffic.recorded_at

    input_data = pd.DataFrame(
        {
            "road_id": [road_id],
            "hour": [recorded_at.hour],
            "day_of_week": [recorded_at.weekday()],
            "month": [recorded_at.month],
        }
    )

    predicted_vehicles = model.predict(input_data)[0]

    if predicted_vehicles >= 50:
        level = "HIGH"
        confidence = 0.88

    elif predicted_vehicles >= 25:
        level = "MEDIUM"
        confidence = 0.72

    else:
        level = "LOW"
        confidence = 0.60

    return {
        "road_id": road_id,
        "predicted_level": level,
        "confidence": confidence,
        "generated_by": "random-forest-v1",
    }