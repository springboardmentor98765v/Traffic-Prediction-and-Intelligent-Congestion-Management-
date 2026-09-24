from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.ai import AnomalyItem, RecommendationItem
from app.services import ai_insights_service

router = APIRouter()


@router.get(
    "/anomalies",
    response_model=List[AnomalyItem],
    summary="Anomaly & Potential Incident Detection (FR-02)",
    description=(
        "Detect anomalous traffic patterns by comparing live traffic telemetry against "
        "model-v1 predictive baselines. Unusual speed drops or unexpected density spikes "
        "are flagged as potential accidents/incidents."
    )
)
def get_traffic_anomalies(
    auto_alert: bool = Query(True, description="Automatically trigger accident alerts in Alert Service for high-severity anomalies"),
    db: Session = Depends(get_db)
):
    return ai_insights_service.detect_anomalies(db=db, auto_trigger_alerts=auto_alert)


@router.get(
    "/recommendations",
    response_model=List[RecommendationItem],
    summary="AI-Based Traffic Recommendations (FR-08)",
    description=(
        "Generate intelligent, explainable recommendations built on the Milestone 2 trained model "
        "and Milestone 3 trend analysis (e.g. suggested departure windows, alternate routes, and delay mitigations)."
    )
)
def get_recommendations(
    road_id: Optional[str] = Query(None, description="Optional target road ID (e.g. R001) for corridor-specific advice")
):
    return ai_insights_service.get_ai_recommendations(road_id=road_id)
