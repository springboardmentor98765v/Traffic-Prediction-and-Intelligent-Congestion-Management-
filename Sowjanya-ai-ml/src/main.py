from fastapi import FastAPI, HTTPException
from congestion_predictor import predict_congestion as get_prediction
from typing import Optional
import pandas as pd

app = FastAPI(title="TrafficVision AI Engine")

traffic_data = pd.read_csv("../data/processed_traffic.csv")


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

        density = float(latest_record["density"])

        timestamp = pd.to_datetime(
            latest_record["timestamp"]
        )

        hour = int(timestamp.hour)

    prediction = get_prediction(density, hour)

    return {
        "road_id": road_id,
        "predicted_level": prediction,
        "confidence": 0.80,
        "generated_by": "heuristic-v0"
    }
