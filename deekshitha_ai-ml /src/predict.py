from pydantic import BaseModel


# ============================================================
# Frozen Milestone 1 API Response Contract
# ============================================================

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
    """
    Milestone 1 heuristic/rule-based congestion prediction.

    This is NOT the final ML model.
    It will be replaced by a trained ML model in Milestone 2.
    """

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
# Gateway Prediction Helper
# ============================================================

def predict_for_road(
    road_id: str,
    vehicle_count: float,
    density: float,
    avg_speed_kmph: float = 0,
) -> CongestionResponse:
    """
    Generates the frozen Milestone 1 prediction response
    for a particular road.
    """

    predicted_level, reason = predict_congestion(
        vehicle_count=vehicle_count,
        density=density,
        avg_speed_kmph=avg_speed_kmph,
    )

    return CongestionResponse(
        road_id=road_id,
        predicted_level=predicted_level,
        confidence=0.85,
        generated_by="heuristic-v0",
    )
