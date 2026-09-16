from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List, Dict, Any

from app.middleware.auth_middleware import get_optional_current_user
from app.models.user import User
from app.schemas.traffic import HistoricalTrafficRecord, TrafficAggregateResponse
from app.schemas.route import RoadConditionResponse
from app.services import traffic_service, road_condition_service

router = APIRouter()


@router.get("/live", summary="Get live traffic for all monitored roads")
def get_live_traffic(current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Returns real-time traffic condition for all monitored road segments.
    Available to public commuters and authenticated operators/admins.
    """
    return traffic_service.get_live_traffic_data()


@router.get("/road/{road_id}", summary="Get traffic details and history for a specific road")
def get_road_traffic(road_id: str, current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Returns detailed current and historical hourly traffic for a given road ID (e.g. R001).
    """
    road_data = traffic_service.get_road_detail(road_id)
    if not road_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found. Monitored roads are R001 to R005."
        )
    return road_data


@router.get("/density", summary="Get aggregated density metrics for dashboard KPIs")
def get_density_metrics(current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Returns aggregated city-wide traffic density metrics, total roads, and congested roads count.
    """
    return traffic_service.get_density_summary()


@router.get(
    "/history",
    response_model=List[HistoricalTrafficRecord],
    summary="Query historical traffic time-series data (FR-01, Section 7.1)"
)
def get_traffic_history(
    road_id: Optional[str] = Query(None, description="Optional road ID filter (e.g. R001)"),
    start: Optional[str] = Query(None, description="Start timestamp filter (ISO string, e.g. 2026-08-20 00:00:00)"),
    end: Optional[str] = Query(None, description="End timestamp filter (ISO string, e.g. 2026-08-27 23:59:59)"),
    limit: int = Query(200, ge=1, le=2000, description="Max records to return"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns historical traffic readings for trend analysis, model evaluation, and analytics charts.
    """
    return traffic_service.get_traffic_history(road_id=road_id, start=start, end=end, limit=limit)


@router.get(
    "/aggregate",
    response_model=TrafficAggregateResponse,
    summary="Get rolled-up aggregate traffic metrics (hour or day) (Section 7.1)"
)
def get_traffic_aggregates(
    road_id: Optional[str] = Query(None, description="Optional road ID filter (e.g. R001)"),
    granularity: str = Query("hour", pattern="^(hour|day)$", description="Aggregation granularity: hour or day"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns aggregate averages (density, vehicle count, speed, peak hour, congestion distribution)
    over the historical observation window.
    """
    return traffic_service.get_traffic_aggregates(road_id=road_id, granularity=granularity)


@router.get(
    "/road-condition/{road_id}",
    response_model=RoadConditionResponse,
    summary="Get road-condition flags (closures, construction, hazards) (Section 7.1)"
)
def get_traffic_road_condition(
    road_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns current status and hazard notes for a road corridor (Section 7.1).
    """
    cond = road_condition_service.get_road_condition(road_id)
    if not cond:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road condition for '{road_id}' not found"
        )
    return cond
