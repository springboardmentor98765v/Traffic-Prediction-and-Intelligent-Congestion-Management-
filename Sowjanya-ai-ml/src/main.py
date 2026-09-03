from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException

from congestion_predictor import predict_congestion as get_prediction


app = FastAPI(title="TrafficVision AI Engine")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CSV_PATH = (
    BASE_DIR
    / "Komal_Data-Engineering-Traffic-Monitoring"
    / "processed_traffic.csv"
)

try:
    traffic_data = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    raise RuntimeError(
        f"processed_traffic.csv not found at: {CSV_PATH}"
    )


@app.get("/")
def home():
    return {
        "message": "TrafficVision AI Engine is running"
    }


@app.get("/api/v1/predict/congestion")
def predict_congestion(
    road_id: str,
    density: Optional[float] = None,
    hour: Optional[int] = None
):
 
    road_data = traffic_data[
        traffic_data["road_id"] == road_id
    ]

    if road_data.empty:
        raise HTTPException(
            status_code=404,
            detail="Road ID not found"
        )
    if density is None or hour is None:
        latest_record = road_data.iloc[-1]

        if density is None:
            density = float(latest_record["density"])

        if hour is None:
            timestamp = pd.to_datetime(
                latest_record["timestamp"]
            )
            hour = int(timestamp.hour)

    prediction = get_prediction(
        density=density,
        hour=hour
    )

    return {
        "road_id": road_id,
        "predicted_level": prediction,
        "confidence": 0.80,
        "generated_by": "heuristic-v0"
    }
