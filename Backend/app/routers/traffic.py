from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any

from app.middleware.auth_middleware import get_optional_current_user, get_current_user
from app.models.user import User
from app.services import traffic_service

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
