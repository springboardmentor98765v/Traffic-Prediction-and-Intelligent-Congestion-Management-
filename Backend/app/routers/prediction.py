from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from typing import Optional
from datetime import datetime
import io
import csv

from app.middleware.auth_middleware import get_optional_current_user
from app.models.user import User
from app.schemas.prediction import (
    CongestionPredictionResponse,
    PeakHoursResponse,
    DelayEstimateResponse,
    PredictionReportResponse
)
from app.services import ml_prediction_service, prediction_service, traffic_service

router = APIRouter()


@router.get(
    "/congestion",
    response_model=CongestionPredictionResponse,
    summary="Predict congestion level for a road segment (Trained ML Model-v1)"
)
def predict_congestion(
    road_id: str = Query(..., description="Road ID to predict congestion for (e.g. R001)"),
    time: Optional[str] = Query(None, description="Optional ISO timestamp or HH:MM string"),
    density: Optional[float] = Query(None, description="Optional current density override (0-100)"),
    hour: Optional[int] = Query(None, ge=0, le=23, description="Optional hour of day override (0-23)"),
    model_version: Optional[str] = Query(None, description="Target model version (e.g. model-v1 or heuristic-v0)"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Milestone 2 Real ML Prediction Endpoint (model-v1).
    Uses trained scikit-learn classifier on multi-week traffic patterns,
    with confidence estimation, peak-hour awareness, and heuristic safety fallback.
    """
    # Parse time parameter if provided
    if time and hour is None:
        try:
            if ":" in time and "T" not in time and " " not in time:
                hour = int(time.split(":")[0])
            else:
                dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
                hour = dt.hour
        except Exception:
            pass

    # Support legacy heuristic when requested explicitly
    if model_version == "heuristic-v0":
        result = prediction_service.predict_congestion(road_id=road_id, density=density, hour=hour)
    else:
        result = ml_prediction_service.predict_congestion(road_id=road_id, density=density, hour=hour)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found. Available road IDs: R001, R002, R003, R004, R005"
        )
    return result


@router.get(
    "/peak-hours",
    response_model=PeakHoursResponse,
    summary="Forecast peak-hour congestion windows for a road"
)
def get_peak_hours(
    road_id: str = Query(..., description="Road ID to forecast peak hours for (e.g. R001)"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Forecasts statistical peak-hour congestion intervals (start, end, severity)
    for the specified road segment based on historical traffic trends.
    """
    result = ml_prediction_service.get_peak_hours(road_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found. Monitored roads: R001 to R005"
        )
    return result


@router.get(
    "/delay",
    response_model=DelayEstimateResponse,
    summary="Estimate traffic delay in minutes for a road segment"
)
def get_delay_estimate(
    road_id: str = Query(..., description="Road ID to estimate delay for (e.g. R001)"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Estimates travel delay in minutes by evaluating current and ML-predicted speed
    against the segment's free-flow speed limit.
    """
    result = ml_prediction_service.estimate_delay(road_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found. Monitored roads: R001 to R005"
        )
    return result


@router.get(
    "/report",
    summary="Generate downloadable traffic prediction report (FR-09)"
)
def get_prediction_report(
    road_id: str = Query(..., description="Road ID to generate prediction report for"),
    format: str = Query("json", pattern="^(json|csv)$", description="Report format: json or csv"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Generates a full 24-hour traffic prediction report for a given corridor,
    including forecasted congestion hourly curve, peak windows, and expected delays.
    Directly supports frontend prediction report downloads.
    """
    report = ml_prediction_service.generate_prediction_report(road_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found"
        )

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Road ID", "Road Name", "Generated At", "Model Version", "Current Level", "Confidence", "Est Delay (min)"])
        writer.writerow([
            report["road_id"], report["road_name"], report["generated_at"],
            report["model_version"], report["current_level"], report["confidence"],
            report["estimated_delay_minutes"]
        ])
        writer.writerow([])
        writer.writerow(["Hour", "Time", "Predicted Level", "Density", "Confidence"])
        for h in report["hourly_forecast"]:
            writer.writerow([h["hour"], h["time"], h["predicted_level"], h["density"], h["confidence"]])

        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=traffic_prediction_{road_id}.csv"}
        )

    return report


@router.get(
    "/live",
    summary="Congestion predictions for all monitored roads (model-v1)"
)
def predict_live(
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns real-time ML-predicted congestion for all live monitored roads.
    """
    live_traffic = traffic_service.get_live_traffic_data()
    predictions = []
    for road in live_traffic:
        pred = ml_prediction_service.predict_congestion(
            road_id=road["road_id"],
            density=road["density"]
        )
        if pred:
            predictions.append(pred)

    return {
        "source": "TrafficVision AI Engine (model-v1)",
        "model_version": "model-v1",
        "total_records": len(predictions),
        "predictions": predictions
    }
