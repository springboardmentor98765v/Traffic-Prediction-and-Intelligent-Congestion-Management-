from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.middleware.auth_middleware import get_optional_current_user
from app.models.user import User
from app.services import prediction_service, traffic_service

router = APIRouter()


@router.get("/congestion", summary="Heuristic congestion prediction for a road")
def predict_congestion(
    road_id: str = Query(..., description="Road ID to predict congestion for (e.g. R001)"),
    density: Optional[float] = Query(None, description="Optional current density override (0-100)"),
    hour: Optional[int] = Query(None, ge=0, le=23, description="Optional hour of day override (0-23)"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Milestone 1 Heuristic Congestion Prediction Stub.
    Uses rule-based thresholds and time-of-day peak hour adjustments (heuristic-v0).
    Placeholder unblocking frontend/QA ahead of trained ML model in Milestone 2.
    """
    result = prediction_service.predict_congestion(road_id=road_id, density=density, hour=hour)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found. Available road IDs: R001, R002, R003, R004, R005"
        )
    return result


@router.get("/live", summary="Congestion predictions for all monitored roads")
def predict_live(current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Returns heuristic congestion predictions for all live monitored roads.
    """
    live_traffic = traffic_service.get_live_traffic_data()
    predictions = []
    for road in live_traffic:
        pred = prediction_service.predict_congestion(
            road_id=road["road_id"],
            density=road["density"]
        )
        if pred:
            predictions.append(pred)

    return {
        "source": "AI Engine Heuristic Stub (Milestone 1)",
        "total_records": len(predictions),
        "predictions": predictions
    }
