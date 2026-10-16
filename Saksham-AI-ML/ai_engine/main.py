"""
TrafficVision AI Inference Microservice (Milestone 2).
Serves real-time ML congestion, peak-hour detection, and travel delay predictions.
Frozen API Contracts for Intern 1 & Intern 4.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from ai_engine.anomaly_detection import detect_anomaly
from ai_engine.feature_engineering import extract_time_features
from ai_engine.recommendations import generate_recommendation
from ai_engine.routing import rank_candidate_routes


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "traffic_model_v2.joblib"
model_artifact: Optional[Dict[str, Any]] = None


def init_model():
    global model_artifact

    if MODEL_PATH.exists():
        model_artifact = joblib.load(str(MODEL_PATH))
        print(
            f"Traffic ML Model v2 loaded successfully from {MODEL_PATH}."
        )
    else:
        print(
            f"Warning: Model artifact not found at {MODEL_PATH}."
        )


init_model()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if model_artifact is None:
        init_model()
    yield


app = FastAPI(
    title="TrafficVision AI Inference Engine",
    version="2.0.0",
    description=(
        "Microservice providing ML-powered congestion classification, "
        "delay estimation, and peak-hour detection."
    ),
    lifespan=lifespan,
)


def run_model_inference(
    road_id: str,
    time_str: Optional[str],
    density: float,
    vehicle_count: int,
):
    if not model_artifact:
        raise HTTPException(
            status_code=503,
            detail="Model artifact is not loaded.",
        )

    if time_str:
        try:
            dt = datetime.fromisoformat(time_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid ISO timestamp format.",
            )
    else:
        dt = datetime.now()

    time_feats = extract_time_features(dt)

    features_dict = {
        "hour_of_day": time_feats["hour_of_day"],
        "day_of_week": time_feats["day_of_week"],
        "is_weekend": time_feats["is_weekend"],
        "is_rush_hour": time_feats["is_rush_hour"],
        "density": density,
        "vehicle_count": vehicle_count,
        "rolling_avg_density": density,
        "rolling_avg_vehicle_count": vehicle_count,
    }

    feature_cols = model_artifact["feature_cols"]
    input_df = pd.DataFrame([features_dict])[feature_cols]

    clf = model_artifact["classifier"]
    class_pred = str(clf.predict(input_df)[0])
    probs = clf.predict_proba(input_df)[0]
    confidence = float(max(probs))

    reg = model_artifact["regressor"]
    delay_pred = float(reg.predict(input_df)[0])

    return {
        "road_id": str(road_id),
        "predicted_level": class_pred,
        "confidence": round(confidence, 4),
        "estimated_delay_minutes": round(
            max(0.0, delay_pred), 1
        ),
        "is_rush_hour": bool(time_feats["is_rush_hour"]),
        "timestamp": dt.isoformat(),
        "model_version": model_artifact.get(
            "model_version",
            "model-v1",
        ),
        "data_source": "trained-random-forest",
    }


# Contract 1: GET /predict/congestion
@app.get("/predict/congestion")
def predict_congestion(
    road_id: str = Query(
        ...,
        description="Identifier of the road segment",
    ),
    time: Optional[str] = Query(
        None,
        description="ISO-8601 timestamp string",
    ),
    density: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
        description="Normalized traffic density",
    ),
    vehicle_count: int = Query(
        50,
        ge=0,
        description="Observed vehicle count",
    ),
):
    res = run_model_inference(
        road_id,
        time,
        density,
        vehicle_count,
    )

    return {
        "road_id": res["road_id"],
        "predicted_level": res["predicted_level"],
        "confidence": res["confidence"],
        "model_version": res["model_version"],
        "timestamp": res["timestamp"],
        "data_source": res["data_source"],
    }


# Contract 2: GET /predict/delay
@app.get("/predict/delay")
def predict_delay(
    road_id: str = Query(
        ...,
        description="Identifier of the road segment",
    ),
    time: Optional[str] = Query(
        None,
        description="ISO-8601 timestamp string",
    ),
    density: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
        description="Normalized traffic density",
    ),
    vehicle_count: int = Query(
        50,
        ge=0,
        description="Observed vehicle count",
    ),
):
    res = run_model_inference(
        road_id,
        time,
        density,
        vehicle_count,
    )

    return {
        "road_id": res["road_id"],
        "estimated_delay_minutes": res[
            "estimated_delay_minutes"
        ],
        "is_rush_hour": res["is_rush_hour"],
        "confidence": res["confidence"],
        "model_version": res["model_version"],
        "timestamp": res["timestamp"],
    }


# Contract 3: GET /predict/peak-hours
@app.get("/predict/peak-hours")
def get_peak_hour_status(
    hour: int = Query(..., ge=0, le=23),
):
    is_peak = (8 <= hour <= 11) or (17 <= hour <= 20)

    desc = (
        "Morning/Evening rush hour"
        if is_peak
        else "Non-peak transit window"
    )

    return {
        "hour": hour,
        "is_peak": is_peak,
        "description": desc,
    }


class SegmentInput(BaseModel):
    road_id: str
    base_duration_min: float = Field(..., ge=0.0)
    density: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
    )
    vehicle_count: int = Field(
        50,
        ge=0,
    )


class RouteCandidateInput(BaseModel):
    route_id: str
    segments: list[SegmentInput]


class RouteRankRequest(BaseModel):
    timestamp: Optional[str] = None
    candidate_routes: list[RouteCandidateInput]


# Contract 4 (Day 5): Route-Ranking Logic
# for Intern 1 & Intern 4
@app.post("/predict/routes/rank")
def rank_routes_endpoint(
    payload: RouteRankRequest,
):
    candidates_dict = [
        {
            "route_id": r.route_id,
            "segments": [
                seg.model_dump()
                for seg in r.segments
            ],
        }
        for r in payload.candidate_routes
    ]

    ranked = rank_candidate_routes(
        candidate_routes=candidates_dict,
        current_time=payload.timestamp,
        predict_fn=run_model_inference,
    )

    return {
        "status": "success",
        "timestamp": (
            payload.timestamp
            or datetime.now().isoformat()
        ),
        "total_routes_evaluated": len(ranked),
        "ranked_routes": ranked,
    }


# M3 Day 3: AI Anomaly Detection
@app.get("/ai/anomalies")
def detect_traffic_anomaly(
    road_id: str = Query(...),
    expected_level: str = Query(...),
    observed_level: str = Query(...),
    time: Optional[str] = Query(None),
):
    is_anomaly = detect_anomaly(
        expected_level,
        observed_level,
    )

    event_time = (
        time
        or datetime.now().isoformat()
    )

    if is_anomaly:
        import os

        alert_url = os.getenv(
            "ALERT_SERVICE_URL",
            "http://127.0.0.1:8003",
        ).rstrip("/") + "/api/v1/alerts"

        try:
            requests.post(
                alert_url,
                json={
                    "type": "accident",
                    "severity": "high",
                    "road_id": road_id,
                    "message": (
                        "Possible traffic incident detected."
                    ),
                },
                timeout=5,
            ).raise_for_status()
        except requests.RequestException as exc:
            print(f"WARNING: Anomaly detected, but alert delivery failed: {exc}")

    return {
        "road_id": road_id,
        "time": event_time,
        "expected_level": expected_level.upper(),
        "observed_level": observed_level.upper(),
        "flagged_as": (
            "possible_incident"
            if is_anomaly
            else None
        ),
    }


# M3 Day 4: AI Recommendations
@app.get("/api/v1/ai/recommendations")
def get_ai_recommendations(
    road_id: str = Query(...),
    time: Optional[str] = Query(None),
    density: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
    ),
    vehicle_count: int = Query(
        50,
        ge=0,
    ),
):
    prediction = run_model_inference(
        road_id=road_id,
        time_str=time,
        density=density,
        vehicle_count=vehicle_count,
    )

    recommendation = generate_recommendation(
        predicted_level=prediction["predicted_level"],
        estimated_delay_minutes=prediction[
            "estimated_delay_minutes"
        ],
    )

    return {
        "road_id": road_id,
        "recommendation_text": (
            recommendation["recommendation_text"]
        ),
        "based_on": recommendation["based_on"],
    }