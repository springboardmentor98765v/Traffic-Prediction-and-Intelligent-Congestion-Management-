from datetime import datetime
from typing import Dict, Any, Optional
from app.services import traffic_service


def predict_by_density(density: float) -> str:
    if density < 20.0:
        return "Low"
    elif density <= 50.0:
        return "Medium"
    else:
        return "High"


def adjust_for_time(congestion: str, hour: int) -> str:
    # Peak traffic hours in cities: Morning 7-10, Evening 17-20
    if (7 <= hour <= 10) or (17 <= hour <= 20):
        if congestion == "Low":
            return "Medium"
        elif congestion == "Medium":
            return "High"
    return congestion


def predict_congestion(
    road_id: str,
    density: Optional[float] = None,
    hour: Optional[int] = None
) -> Dict[str, Any]:
    norm_id = road_id.upper()
    road_info = traffic_service.get_road_detail(norm_id)
    if not road_info and norm_id not in traffic_service.ROAD_NAMES:
        return None

    if density is None:
        density = road_info["density"] if road_info else 35.0

    if hour is None:
        hour = datetime.utcnow().hour

    base_level = predict_by_density(density)
    predicted_level = adjust_for_time(base_level, hour)

    return {
        "road_id": norm_id,
        "road_name": traffic_service.ROAD_NAMES.get(norm_id, norm_id),
        "predicted_level": predicted_level,
        "confidence": 0.80,
        "current_density": round(float(density), 2),
        "time_of_day": hour,
        "generated_by": "heuristic-v0"
    }
