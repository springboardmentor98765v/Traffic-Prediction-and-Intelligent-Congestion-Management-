from pathlib import Path
from datetime import datetime
import joblib
import pandas as pd

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.traffic_service import (
    get_road_traffic,
    get_postgres_connection,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(tags=["AI Engine"])


# ============================================================
# MODEL PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ai-engine" / "models" / "model-v1.joblib"

# ============================================================
# LOAD TRAINED M2 MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found at: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


# ============================================================
# API RESPONSE MODELS
# ============================================================

class CongestionResponse(BaseModel):
    road_id: str
    predicted_level: str
    confidence: float
    model_version: str


class PeakWindow(BaseModel):
    start: str
    end: str


class PeakHoursResponse(BaseModel):
    road_id: str
    peak_windows: list[PeakWindow]


class DelayResponse(BaseModel):
    road_id: str
    estimated_delay_minutes: float
    confidence: float


# ============================================================
# LEGACY POST REQUEST
# Kept for backward compatibility
# ============================================================

class CongestionRequest(BaseModel):
    road_id: str
    vehicle_count: float
    density: float
    avg_speed_kmph: float
    road_capacity: float
    road_length_km: float
    hour: int
    day_of_week: int
    is_weekend: int


# ============================================================
# M2 ML CONGESTION PREDICTOR
# ============================================================

def predict_congestion(
    vehicle_count: float,
    density: float,
    avg_speed_kmph: float,
    road_capacity: float,
    road_length_km: float,
    hour: int,
    day_of_week: int,
    is_weekend: int,
    road_id: str,
) -> tuple[str, float]:

    input_data = pd.DataFrame(
        [
            {
                "vehicle_count": vehicle_count,
                "avg_speed_kmph": avg_speed_kmph,
                "road_capacity": road_capacity,
                "road_length_km": road_length_km,
                "traffic_density_vehicles_per_km": density,
                "hour": hour,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "road_id": road_id,
            }
        ]
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    confidence = float(probabilities.max())

    return prediction, confidence


# ============================================================
# STATIC ROAD METADATA
# ============================================================

def get_road_metadata(road_id: str) -> tuple[float, float]:
    """
    Get static road_capacity and road_length_km from the roads table.
    """
    connection = get_postgres_connection()

    if connection is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable",
        )

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT road_capacity, road_length_km
            FROM roads
            WHERE road_id = %s
            LIMIT 1
            """,
            (road_id,),
        )
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Road '{road_id}' not found",
            )

        return float(row[0] if row[0] is not None else 1000.0), float(row[1] if row[1] is not None else 5.0)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load road metadata: {exc}",
        )
    finally:
        if cursor is not None:
            cursor.close()


# ============================================================
# BUILD MODEL FEATURES FROM LIVE TRAFFIC + ROAD METADATA
# ============================================================

def get_prediction_features(road_id: str):
    traffic = get_road_traffic(road_id)

    if not traffic or not traffic.get("history"):
        raise HTTPException(
            status_code=404,
            detail=f"No traffic reading found for road '{road_id}'",
        )

    road_capacity, road_length_km = get_road_metadata(road_id)

    latest = traffic["history"][0]

    vehicle_count = float(latest.get("vehicle_count", latest.get("vehicles", 100.0)))
    density = float(
        latest.get(
            "traffic_density_vehicles_per_km",
            latest.get("density", 0.0),
        )
    )
    avg_speed = float(
        latest.get(
            "avg_speed_kmph",
            latest.get("avg_speed", latest.get("speed", 45.0)),
        )
    )

    timestamp = latest.get("updated_at")

    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

    if timestamp is None:
        timestamp = datetime.now()

    hour = timestamp.hour
    day_of_week = timestamp.weekday()
    is_weekend = int(day_of_week >= 5)

    return {
        "vehicle_count": vehicle_count,
        "density": density,
        "avg_speed_kmph": avg_speed,
        "road_capacity": road_capacity,
        "road_length_km": road_length_km,
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
    }


# ============================================================
# CONGESTION — DOCUMENTED GET CONTRACT
# ============================================================

@router.get(
    "/congestion",
    response_model=CongestionResponse,
)
def get_congestion_prediction(
    road_id: str = Query(...),
    time: str | None = Query(None),
):
    features = get_prediction_features(road_id)

    if time:
        try:
            requested_time = datetime.fromisoformat(
                time.replace("Z", "+00:00")
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid time format. Use ISO-8601 format.",
            )

        features["hour"] = requested_time.hour
        features["day_of_week"] = requested_time.weekday()
        features["is_weekend"] = int(
            requested_time.weekday() >= 5
        )

    predicted_level, confidence = predict_congestion(
        road_id=road_id,
        **features,
    )

    return CongestionResponse(
        road_id=road_id,
        predicted_level=predicted_level,
        confidence=round(confidence, 4),
        model_version="model-v1",
    )


# ============================================================
# CONGESTION — LEGACY POST CONTRACT
# ============================================================

@router.post("/congestion")
def get_congestion_prediction_post(
    request: CongestionRequest,
):
    predicted_level, confidence = predict_congestion(
        vehicle_count=request.vehicle_count,
        density=request.density,
        avg_speed_kmph=request.avg_speed_kmph,
        road_capacity=request.road_capacity,
        road_length_km=request.road_length_km,
        hour=request.hour,
        day_of_week=request.day_of_week,
        is_weekend=request.is_weekend,
        road_id=request.road_id,
    )

    return {
        "road_id": request.road_id,
        "predicted_level": predicted_level,
        "confidence": round(confidence, 4),
        "model_version": "model-v1",
    }


# ============================================================
# PEAK HOURS
# ============================================================

@router.get(
    "/peak-hours",
    response_model=PeakHoursResponse,
)
def get_peak_hours(
    road_id: str = Query(...),
):
    get_road_traffic(road_id)

    return PeakHoursResponse(
        road_id=road_id,
        peak_windows=[
            PeakWindow(start="08:00", end="10:00"),
            PeakWindow(start="17:00", end="20:00"),
        ],
    )


# ============================================================
# DELAY
# ============================================================

@router.get(
    "/delay",
    response_model=DelayResponse,
)
def get_delay(
    road_id: str = Query(...),
):
    features = get_prediction_features(road_id)

    speed = features["avg_speed_kmph"]
    length = features["road_length_km"]
    reference_speed = 50.0

    if speed <= 0:
        delay = 0.0
        confidence = 0.0
    else:
        current_travel_time = (length / speed) * 60
        free_flow_time = (length / reference_speed) * 60

        delay = max(
            0.0,
            current_travel_time - free_flow_time,
        )

        confidence = min(
            0.99,
            max(0.50, speed / reference_speed),
        )

    return DelayResponse(
        road_id=road_id,
        estimated_delay_minutes=round(delay, 2),
        confidence=round(confidence, 4),
    )