from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.rbac import require_role
from app.database.connection import get_db
from app.database.models import User
from app.prediction.schemas import PredictionResponse
from app.prediction.service import predict_congestion

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)


@router.get(
    "/congestion",
    response_model=PredictionResponse,
)
def congestion_prediction(
    road_id: int,
    current_user: User = Depends(require_role("admin", "operator", "public")),
    db: Session = Depends(get_db),
):
    prediction = predict_congestion(
        db,
        road_id,
    )

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="No traffic data found for road",
        )

    return prediction
