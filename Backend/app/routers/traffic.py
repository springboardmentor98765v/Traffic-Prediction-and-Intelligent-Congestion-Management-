from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import random

from app.middleware.auth_middleware import get_current_user, require_role
from app.models.user import User

router = APIRouter()


@router.get("/live")
def get_live_traffic(current_user: User = Depends(get_current_user)):
    roads = []
    for i in range(1, 6):
        vehicle_count = random.randint(10, 200)
        density = round(random.uniform(5.0, 80.0), 2)
        if density < 20:
            congestion_level = "Low"
        elif density <= 50:
            congestion_level = "Medium"
        else:
            congestion_level = "High"
        roads.append({
            "road_id": f"road_{i}",
            "vehicle_count": vehicle_count,
            "density": density,
            "congestion_level": congestion_level,
            "updated_at": datetime.utcnow().isoformat()
        })
    return roads


@router.get("/road/{road_id}")
def get_road_traffic(road_id: str, current_user: User = Depends(get_current_user)):
    vehicle_count = random.randint(10, 200)
    density = round(random.uniform(5.0, 80.0), 2)
    if density < 20:
        congestion_level = "Low"
    elif density <= 50:
        congestion_level = "Medium"
    else:
        congestion_level = "High"

    history = []
    for h in range(24):
        hist_density = round(random.uniform(5.0, 80.0), 2)
        if hist_density < 20:
            hist_level = "Low"
        elif hist_density <= 50:
            hist_level = "Medium"
        else:
            hist_level = "High"
        history.append({
            "hour": h,
            "density": hist_density,
            "congestion_level": hist_level
        })

    return {
        "road_id": road_id,
        "name": f"Road {road_id.replace('road_', 'R')}",
        "congestion_level": congestion_level,
        "vehicle_count": vehicle_count,
        "density": density,
        "history": history
    }


@router.get("/density")
def get_density_metrics(current_user: User = Depends(get_current_user)):
    return {
        "average_density": round(random.uniform(20.0, 60.0), 2),
        "total_roads": 5,
        "congested_roads": random.randint(1, 3),
        "timestamp": datetime.utcnow().isoformat()
    }
