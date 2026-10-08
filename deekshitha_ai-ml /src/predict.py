from pathlib import Path
from datetime import datetime
import joblib
import pandas as pd

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(tags=["AI Engine"])


# ============================================================
# MODEL PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ai-engine" / "models" / "model-v1.joblib"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found at: {MODEL_PATH}"
    )


# ============================================================
# LOAD TRAINED M2 MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# RESPONSE MODELS
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
# CONGESTION PREDICTOR
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

    return str(prediction), confidence


# ============================================================
# CONGESTION PREDICTION
# ============================================================

@router.get(
    "/congestion",
    response_model=CongestionResponse
)
def get_congestion_prediction(
    road_id: str,
    time: str | None = None,
):
    """
    Predict congestion for a road.

    Final API contract:
    GET /api/v1/predict/congestion?road_id={id}&time={ts}
    """

    # --------------------------------------------------------
    # NOTE:
    # The integrated backend should obtain the latest traffic
    # features for the requested road_id.
    #
    # This fallback block is intentionally kept simple until
    # the backend traffic-data service is connected.
    # --------------------------------------------------------

    raise HTTPException(
        status_code=501,
        detail=(
            "Congestion endpoint requires traffic feature "
            "integration for the requested road_id."
        ),
    )


# ============================================================
# PEAK-HOUR PREDICTION
# ============================================================

@router.get(
    "/peak-hours",
    response_model=PeakHoursResponse
)
def get_peak_hours(
    road_id: str,
):
    """
    Return the peak traffic windows for a road.

    Final API contract:
    GET /api/v1/predict/peak-hours?road_id={id}
    """

    return PeakHoursResponse(
        road_id=road_id,
        peak_windows=[
            PeakWindow(start="08:00", end="10:00"),
            PeakWindow(start="17:00", end="20:00"),
        ],
    )


# ============================================================
# DELAY PREDICTION
# ============================================================

@router.get(
    "/delay",
    response_model=DelayResponse
)
def get_delay_prediction(
    road_id: str,
):
    """
    Estimate delay for a road.

    Final API contract:
    GET /api/v1/predict/delay?road_id={id}
    """

    raise HTTPException(
        status_code=501,
        detail=(
            "Delay endpoint requires traffic speed and "
            "road-length integration for the requested road_id."
        ),
    )
