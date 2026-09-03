from fastapi import APIRouter, Depends, Query
from datetime import datetime
import random

from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/congestion")
def predict_congestion(
    road_id: str = Query(..., description="Road ID to predict congestion for"),
    current_user: User = Depends(get_current_user)
):
    density = round(random.uniform(5.0, 80.0), 2)
    hour = datetime.utcnow().hour

    if density < 20:
        predicted_level = "Low"
        confidence = round(random.uniform(0.7, 0.9), 2)
    elif density <= 50:
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            predicted_level = "High"
            confidence = round(random.uniform(0.6, 0.8), 2)
        else:
            predicted_level = "Medium"
            confidence = round(random.uniform(0.65, 0.85), 2)
    else:
        predicted_level = "High"
        confidence = round(random.uniform(0.75, 0.95), 2)

    return {
        "road_id": road_id,
        "predicted_level": predicted_level,
        "confidence": confidence,
        "current_density": density,
        "time_of_day": hour,
        "generated_by": "heuristic-v0"
    }
