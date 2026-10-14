import os
from datetime import datetime
from typing import Optional
import joblib
import pandas as pd
import httpx  # type: ignore
from fastapi import FastAPI, Query

app = FastAPI(
    title="TrafficVision AI - AI Engine Service",
    description="Trained ML Prediction Service for Traffic Congestion",
    version="2.0.0",
)

DATA_ENGINEERING_URL = "http://127.0.0.1:8000"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "traffic_model.joblib")

# Load trained Random Forest model
model_artifact = None
if os.path.exists(MODEL_PATH):
    model_artifact = joblib.load(MODEL_PATH)


def is_rush_hour(dt: datetime) -> bool:
    hour = dt.hour
    return (8 <= hour <= 11) or (17 <= hour <= 20)


def predict_ml_congestion(
    density: float,
    vehicle_count: float = 120.0,
    avg_speed_kmph: float = 35.0,
    timestamp_str: Optional[str] = None,
) -> tuple[str, float, str]:
    if timestamp_str:
        try:
            dt = datetime.fromisoformat(timestamp_str)
        except ValueError:
            dt = datetime.now()
    else:
        dt = datetime.now()

    hour = dt.hour
    day_of_week = dt.weekday()
    peak_flag = 1 if is_rush_hour(dt) else 0

    if model_artifact:
        model = model_artifact["model"]
        feature_names = model_artifact["features"]

        # Prepare record mapping exactly to trained feature names
        sample_data = {
            "density": [density],
            "vehicle_count": [vehicle_count],
            "avg_speed_kmph": [avg_speed_kmph],
            "hour": [hour],
            "day_of_week": [day_of_week],
            "is_peak_hour": [peak_flag],
        }

        row = pd.DataFrame(sample_data)[[f for f in feature_names if f in sample_data]]
        pred_label = model.predict(row)[0]
        pred_proba = max(model.predict_proba(row)[0])

        return (
            str(pred_label),
            round(float(pred_proba), 2),
            f"Machine learning model classified congestion as {pred_label}",
        )

    # Heuristic fallback if model artifact is missing
    adjusted_density = min(density * (1.15 if peak_flag else 1.0), 1.0)
    if adjusted_density >= 0.70:
        return "HIGH", 0.85, "High density detected (heuristic fallback)"
    elif adjusted_density >= 0.40:
        return "MEDIUM", 0.78, "Moderate density detected (heuristic fallback)"
    return "LOW", 0.75, "Low density detected (heuristic fallback)"


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI Engine Service",
        "version": "2.0.0",
        "ml_model_loaded": model_artifact is not None,
    }


@app.get("/api/v1/predict/congestion", tags=["AI Engine"])
async def predict_congestion(
    road_id: str = Query(..., description="Road identifier (e.g., '1' or 'R001')")
):
    source = "random-forest-v1" if model_artifact else "heuristic-fallback"
    density = 0.50
    live_timestamp = datetime.now().isoformat()
    upstream_connected = False

    numeric_id = "".join(filter(str.isdigit, road_id))
    upstream_id = int(numeric_id) if numeric_id else road_id

    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(f"{DATA_ENGINEERING_URL}/traffic/road/{upstream_id}")
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, list) and len(data) > 0:
                    latest = data[0]
                    if latest.get("density") is not None:
                        density = float(latest["density"])
                    live_timestamp = latest.get("timestamp", live_timestamp)
                    upstream_connected = True
    except Exception:
        upstream_connected = False

    predicted_level, confidence, explanation = predict_ml_congestion(
        density=density, timestamp_str=live_timestamp
    )

    return {
        "road_id": road_id,
        "predicted_level": predicted_level,
        "confidence": confidence,
        "explanation": explanation,
        "density_used": density,
        "peak_hour": is_rush_hour(datetime.fromisoformat(live_timestamp)),
        "data_source": "live-stream" if upstream_connected else "fallback-baseline",
        "generated_by": source,
    }