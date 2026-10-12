from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.prediction.schemas import (
    CongestionPredictionResponse,
    DelayResponse,
    PeakHoursResponse,
)
from app.prediction.service import prediction_service
from app.prediction.schemas import VehicleCountPredictionResponse
from app.prediction.vehicle_count_service import vehicle_count_service

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
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available.")

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
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available.")

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
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available.")

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


@router.get(
    "/vehicle-count",
    response_model=VehicleCountPredictionResponse,
)
def predict_vehicle_count(
    junction: int = Query(ge=1, le=3),
    time: datetime = Query(...),
):
    try:
        return vehicle_count_service.predict(
            junction=junction,
            prediction_time=time,
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Vehicle-count prediction failed: {exc}",
        )
