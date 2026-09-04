from pathlib import Path
from typing import Optional

import httpx
import pandas as pd
from fastapi import FastAPI, HTTPException

from congestion_predictor import predict_congestion as get_prediction


app = FastAPI(
    title="TrafficVision AI Engine",
    description="Traffic congestion prediction using density and peak-hour logic",
    version="1.0.0"
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent

CSV_PATH = (
    BASE_DIR
    / "Komal_Data-Engineering-Traffic-Monitoring"
    / "processed_traffic.csv"
)

TRAFFIC_API_URL = "http://127.0.0.1:8000/traffic/live"


try:
    traffic_data = pd.read_csv(CSV_PATH)

except FileNotFoundError:
    raise RuntimeError(
        f"processed_traffic.csv not found at: {CSV_PATH}"
    )


@app.get(
    "/",
    tags=["AI Engine"],
    summary="Health Check"
)
def home():
    return {
        "message": "TrafficVision AI Engine is running",
        "status": "success"
    }


@app.get(
    "/api/v1/predict/congestion",
    tags=["AI Engine"],
    summary="Congestion Prediction"
)
def predict_congestion(
    road_id: str,
    density: Optional[float] = None,
    hour: Optional[int] = None
):

    road_data = traffic_data[
        traffic_data["road_id"].astype(str) == str(road_id)
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

    if density < 0:
        raise HTTPException(
            status_code=400,
            detail="Density cannot be negative"
        )

    if hour < 0 or hour > 23:
        raise HTTPException(
            status_code=400,
            detail="Hour must be between 0 and 23"
        )

    prediction = get_prediction(
        density=density,
        hour=hour
    )

    return {
        "road_id": road_id,
        "density": density,
        "hour": hour,
        "predicted_level": prediction,
        "confidence": 0.80,
        "generated_by": "heuristic-v0"
    }


@app.get(
    "/api/v1/predict/live",
    tags=["AI Engine"],
    summary="Live Congestion Prediction"
)
def predict_live():

    try:
        response = httpx.get(
            TRAFFIC_API_URL,
            timeout=10
        )

        response.raise_for_status()
        live_data = response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Traffic monitoring API is unavailable"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Traffic monitoring API returned an error"
        )

    traffic_records = live_data.get("traffic", [])

    predictions = []

    for record in traffic_records:

        road_id = record.get("road_id")
        density = record.get("density")
        timestamp = record.get("timestamp")

        if road_id is None or density is None or timestamp is None:
            continue

        try:
            hour = pd.to_datetime(timestamp).hour

            prediction = get_prediction(
                density=float(density),
                hour=int(hour)
            )

            predictions.append({
                "road_id": road_id,
                "density": float(density),
                "hour": int(hour),
                "predicted_level": prediction,
                "confidence": 0.80,
                "generated_by": "heuristic-v0"
            })

        except (ValueError, TypeError):
            continue

    return {
        "source": "Komal Traffic Monitoring API",
        "total_records": len(predictions),
        "predictions": predictions
    }
