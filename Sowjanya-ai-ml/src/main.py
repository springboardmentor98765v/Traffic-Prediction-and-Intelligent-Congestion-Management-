from pathlib import Path
from typing import Optional

import httpx
import pandas as pd
from fastapi import FastAPI, HTTPException

from src.model import predict_congestion_ml


app = FastAPI(
    title="TrafficVision AI Prediction Service",
    description="Traffic congestion prediction using trained Random Forest ML model",
    version="2.0.0"
)


# ---------------------------------------------------------
# MODEL VERSION
# ---------------------------------------------------------

MODEL_VERSION = "random-forest-v1"


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Primary:
# Sowjanya-ai-ml/data/processed_traffic.csv
CSV_PATH = BASE_DIR / "data" / "processed_traffic.csv"

# Fallback:
# Existing team data location
FALLBACK_CSV_PATH = (
    BASE_DIR.parent
    / "Komal_Data-Engineering-Traffic-Monitoring"
    / "processed_traffic.csv"
)


# ---------------------------------------------------------
# LOAD TRAFFIC DATA
# ---------------------------------------------------------

if CSV_PATH.exists():
    traffic_data = pd.read_csv(CSV_PATH)

elif FALLBACK_CSV_PATH.exists():
    traffic_data = pd.read_csv(FALLBACK_CSV_PATH)

else:
    raise RuntimeError(
        "processed_traffic.csv not found."
    )


# Make sure timestamp is datetime
traffic_data["timestamp"] = pd.to_datetime(
    traffic_data["timestamp"]
)


# Create consistent road ID encoding
traffic_data["road_id_encoded"] = (
    traffic_data["road_id"]
    .astype("category")
    .cat.codes
)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get(
    "/",
    tags=["AI Engine"],
    summary="Health Check"
)
def home():
    return {
        "message": "TrafficVision AI Prediction Service is running",
        "status": "success",
        "model_version": MODEL_VERSION
    }


# ---------------------------------------------------------
# CONGESTION PREDICTION
# ---------------------------------------------------------

@app.get(
    "/api/v1/predict/congestion",
    tags=["Prediction"],
    summary="ML Congestion Prediction"
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

    # Use latest record when values are not provided
    latest_record = road_data.iloc[-1]

    if density is None:
        density = float(latest_record["density"])

    if hour is None:
        hour = int(latest_record["timestamp"].hour)

    # Validate density
    if density < 0:
        raise HTTPException(
            status_code=400,
            detail="Density cannot be negative"
        )

    # Validate hour
    if hour < 0 or hour > 23:
        raise HTTPException(
            status_code=400,
            detail="Hour must be between 0 and 23"
        )

    vehicle_count = int(
        latest_record["vehicle_count"]
    )

    avg_speed = float(
        latest_record["avg_speed"]
    )

    day_of_week = int(
        latest_record["timestamp"].dayofweek
    )

    road_id_encoded = int(
        latest_record["road_id_encoded"]
    )

    # -----------------------------------------------------
    # ML PREDICTION
    # -----------------------------------------------------

    result = predict_congestion_ml(
        road_id_encoded=road_id_encoded,
        vehicle_count=vehicle_count,
        avg_speed=avg_speed,
        density=float(density),
        hour=int(hour),
        day_of_week=day_of_week
    )

    return {
        "road_id": road_id,
        "predicted_level": result["prediction"],
        "confidence": result["confidence"],
        "model_version": result.get(
            "model_version",
            MODEL_VERSION
        )
    }


# ---------------------------------------------------------
# PEAK-HOUR FORECAST
# ---------------------------------------------------------

@app.get(
    "/api/v1/predict/peak-hours",
    tags=["Prediction"],
    summary="Peak Hour Forecast"
)
def predict_peak_hours(
    road_id: str
):

    road_data = traffic_data[
        traffic_data["road_id"].astype(str) == str(road_id)
    ]

    if road_data.empty:
        raise HTTPException(
            status_code=404,
            detail="Road ID not found"
        )

    return {
        "road_id": road_id,
        "peak_windows": [
            {
                "start": "07:00",
                "end": "10:00"
            },
            {
                "start": "17:00",
                "end": "20:00"
            }
        ],
        "model_version": MODEL_VERSION
    }


# ---------------------------------------------------------
# DELAY ESTIMATION
# ---------------------------------------------------------

@app.get(
    "/api/v1/predict/delay",
    tags=["Prediction"],
    summary="Traffic Delay Estimation"
)
def predict_delay(
    road_id: str
):

    road_data = traffic_data[
        traffic_data["road_id"].astype(str) == str(road_id)
    ]

    if road_data.empty:
        raise HTTPException(
            status_code=404,
            detail="Road ID not found"
        )

    latest_record = road_data.iloc[-1]

    density = float(
        latest_record["density"]
    )

    hour = int(
        latest_record["timestamp"].hour
    )

    vehicle_count = int(
        latest_record["vehicle_count"]
    )

    avg_speed = float(
        latest_record["avg_speed"]
    )

    day_of_week = int(
        latest_record["timestamp"].dayofweek
    )

    road_id_encoded = int(
        latest_record["road_id_encoded"]
    )

    # -----------------------------------------------------
    # ML PREDICTION
    # -----------------------------------------------------

    result = predict_congestion_ml(
        road_id_encoded=road_id_encoded,
        vehicle_count=vehicle_count,
        avg_speed=avg_speed,
        density=density,
        hour=hour,
        day_of_week=day_of_week
    )

    prediction = result["prediction"]
    confidence = result["confidence"]

    # -----------------------------------------------------
    # INITIAL DELAY ESTIMATION LOGIC
    # -----------------------------------------------------

    if prediction == "Low":
        delay_minutes = 2

    elif prediction == "Medium":
        delay_minutes = 5

    else:
        delay_minutes = 10

    return {
        "road_id": road_id,
        "predicted_level": prediction,
        "estimated_delay_minutes": delay_minutes,
        "confidence": confidence,
        "model_version": result.get(
            "model_version",
            MODEL_VERSION
        )
    }


# ---------------------------------------------------------
# LIVE CONGESTION PREDICTION
# ---------------------------------------------------------

TRAFFIC_API_URL = (
    "http://127.0.0.1:8000/traffic/live"
)


@app.get(
    "/api/v1/predict/live",
    tags=["Prediction"],
    summary="Live ML Congestion Prediction"
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

    traffic_records = live_data.get(
        "traffic",
        []
    )

    predictions = []

    for record in traffic_records:

        road_id = record.get("road_id")
        density = record.get("density")
        timestamp = record.get("timestamp")

        if (
            road_id is None
            or density is None
            or timestamp is None
        ):
            continue

        try:

            road_data = traffic_data[
                traffic_data["road_id"].astype(str)
                == str(road_id)
            ]

            if road_data.empty:
                continue

            latest_record = road_data.iloc[-1]

            parsed_timestamp = pd.to_datetime(
                timestamp
            )

            hour = parsed_timestamp.hour

            vehicle_count = int(
                latest_record["vehicle_count"]
            )

            avg_speed = float(
                latest_record["avg_speed"]
            )

            day_of_week = int(
                parsed_timestamp.dayofweek
            )

            road_id_encoded = int(
                latest_record["road_id_encoded"]
            )

            # -------------------------------------------------
            # ML PREDICTION
            # -------------------------------------------------

            result = predict_congestion_ml(
                road_id_encoded=road_id_encoded,
                vehicle_count=vehicle_count,
                avg_speed=avg_speed,
                density=float(density),
                hour=int(hour),
                day_of_week=day_of_week
            )

            predictions.append({
                "road_id": road_id,
                "density": float(density),
                "hour": int(hour),
                "predicted_level": result["prediction"],
                "confidence": result["confidence"],
                "model_version": result.get(
                    "model_version",
                    MODEL_VERSION
                )
            })

        except (ValueError, TypeError, KeyError):

            continue

    return {
        "source": "Traffic Monitoring API",
        "model_version": MODEL_VERSION,
        "total_records": len(predictions),
        "predictions": predictions
    }
