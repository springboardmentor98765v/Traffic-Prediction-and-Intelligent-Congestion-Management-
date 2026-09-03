from sqlalchemy.orm import Session

from app.traffic.service import get_latest_traffic


def predict_congestion(
    db: Session,
    road_id: int,
):
    traffic = get_latest_traffic(
        db,
        road_id,
    )

    if not traffic:
        return None

    density = traffic.density

    if density >= 0.80:
        level = "HIGH"
        confidence = 0.88

    elif density >= 0.50:
        level = "MEDIUM"
        confidence = 0.72

    else:
        level = "LOW"
        confidence = 0.60

    return {
        "road_id": road_id,
        "predicted_level": level,
        "confidence": confidence,
        "generated_by": "heuristic-v0",
    }
