from pathlib import Path
import joblib
import pandas as pd

from fastapi import APIRouter
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

# ============================================================
# LOAD TRAINED M2 MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found at: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


# ============================================================
# API RESPONSE
# ============================================================

class CongestionResponse(BaseModel):
    road_id: str
    predicted_level: str
    confidence: float
    generated_by: str


# ============================================================
# API REQUEST
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
# CONGESTION PREDICTION ENDPOINT
# ============================================================

@router.post(
    "/congestion",
    response_model=CongestionResponse
)
def get_congestion_prediction(
    request: CongestionRequest
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

    return CongestionResponse(
        road_id=request.road_id,
        predicted_level=predicted_level,
        confidence=round(confidence, 4),
        generated_by="model-v1",
    )
