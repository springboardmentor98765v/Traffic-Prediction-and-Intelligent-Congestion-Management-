from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx


app = FastAPI(
    title="TrafficVision AI Engine",
    description="Traffic congestion prediction service",
    version="1.0.0",
)


# Intern 2 Traffic Monitoring API
TRAFFIC_API_URL = "http://127.0.0.1:8000/api/v1/traffic/live"


# ============================================================
# Request / Response Models
# ============================================================

class TrafficInput(BaseModel):
    vehicle_count: float
    density: float
    avg_speed_kmph: float
    road_id: str
    time_of_day: str


class PredictionResponse(BaseModel):
    road_id: str
    congestion_level: str
    reason: str


class LivePredictionResponse(BaseModel):
    road_id: str
    vehicle_count: float
    density: float
    current_congestion: str
    predicted_congestion: str
    reason: str
    updated_at: str


# Frozen Milestone 1 API contract
class CongestionResponse(BaseModel):
    road_id: str
    predicted_level: str
    confidence: float
    generated_by: str


# ============================================================
# Rule-Based Congestion Predictor
# ============================================================

def predict_congestion(
    vehicle_count: float,
    density: float,
    avg_speed_kmph: float,
) -> tuple[str, str]:

    # Milestone 1: heuristic/rule-based prediction.
    # This will be replaced by a trained ML model in Milestone 2.

    if density >= 20:
        return (
            "High",
            "High traffic density indicates heavy congestion",
        )

    if density >= 10:
        return (
            "Medium",
            "Moderate traffic density indicates increasing congestion",
        )

    return (
        "Low",
        "Traffic density is within a relatively normal range",
    )


# ============================================================
# Health Check
# ============================================================

@app.get("/")
def root():
    return {
        "service": "TrafficVision AI Engine",
        "status": "running",
    }


# ============================================================
# Day 3 - Manual Prediction Endpoint
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict_traffic(data: TrafficInput):

    congestion_level, reason = predict_congestion(
        vehicle_count=data.vehicle_count,
        density=data.density,
        avg_speed_kmph=data.avg_speed_kmph,
    )

    return PredictionResponse(
        road_id=data.road_id,
        congestion_level=congestion_level,
        reason=reason,
    )


# ============================================================
# Day 4 - Live Traffic Prediction
# ============================================================

@app.get(
    "/predict/live",
    response_model=list[LivePredictionResponse]
)
async def predict_live_traffic():

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(TRAFFIC_API_URL)
            response.raise_for_status()

        traffic_data = response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Traffic Monitoring service is unavailable",
        )

    predictions = []

    for road in traffic_data:

        predicted_level, reason = predict_congestion(
            vehicle_count=road["vehicle_count"],
            density=road["density"],
            avg_speed_kmph=0,
        )

        predictions.append(
            LivePredictionResponse(
                road_id=road["road_id"],
                vehicle_count=road["vehicle_count"],
                density=road["density"],
                current_congestion=road["congestion_level"],
                predicted_congestion=predicted_level,
                reason=reason,
                updated_at=road["updated_at"],
            )
        )

    return predictions


# ============================================================
# Gateway Contract
# GET /api/v1/predict/congestion?road_id=R001
# ============================================================

@app.get(
    "/api/v1/predict/congestion",
    response_model=CongestionResponse
)
async def predict_congestion_by_road(
    road_id: str = Query(
        ...,
        description="Road ID such as R001"
    )
):

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(TRAFFIC_API_URL)
            response.raise_for_status()

        traffic_data = response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Traffic Monitoring service is unavailable",
        )

    # Find requested road
    road = next(
        (
            item
            for item in traffic_data
            if item["road_id"] == road_id
        ),
        None,
    )

    if road is None:
        raise HTTPException(
            status_code=404,
            detail=f"Road {road_id} not found",
        )

    # Apply rule-based prediction
    predicted_level, reason = predict_congestion(
        vehicle_count=road["vehicle_count"],
        density=road["density"],
        avg_speed_kmph=0,
    )

    return CongestionResponse(
        road_id=road["road_id"],
        predicted_level=predicted_level,
        confidence=0.85,
        generated_by="heuristic-v0",
    )