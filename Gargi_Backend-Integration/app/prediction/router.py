from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.prediction.schemas import (
    CongestionPredictionResponse,
    DelayResponse,
    PeakHoursResponse,
)
from app.prediction.service import prediction_service

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)


@router.get(
    "/congestion",
    response_model=CongestionPredictionResponse,
)
def predict_congestion(
    road_id: int,
    time: datetime,
    db: Session = Depends(get_db),
):
    try:
        return prediction_service.predict_congestion(
            db=db,
            road_id=road_id,
            prediction_time=time,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        )


@router.get(
    "/peak-hours",
    response_model=PeakHoursResponse,
)
def predict_peak_hours(
    road_id: int,
    db: Session = Depends(get_db),
):
    try:
        return prediction_service.get_peak_hours(
            db=db,
            road_id=road_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Peak-hour prediction failed: {exc}",
        )


@router.get(
    "/delay",
    response_model=DelayResponse,
)
def predict_delay(
    road_id: int,
    db: Session = Depends(get_db),
):
    try:
        return prediction_service.estimate_delay(
            db=db,
            road_id=road_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Delay estimation failed: {exc}",
        )
