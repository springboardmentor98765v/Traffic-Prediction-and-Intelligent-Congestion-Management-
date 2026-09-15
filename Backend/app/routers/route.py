from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from app.middleware.auth_middleware import get_optional_current_user, require_role
from app.models.user import User
from app.schemas.route import (
    RouteOptimizeResponse,
    AlternateRouteItem,
    TravelTimeResponse,
    RoadConditionResponse,
    RoadConditionUpdateRequest
)
from app.services import route_service, road_condition_service

router = APIRouter()


@router.get(
    "/optimize",
    response_model=RouteOptimizeResponse,
    summary="Compute optimized route between origin and destination"
)
def optimize_route(
    origin: str = Query(..., description="Starting point (e.g. '12.9716,77.5946' or 'R001' or 'MG Road')"),
    destination: str = Query(..., description="Destination point (e.g. '12.9352,77.6245' or 'R002' or 'Ring Road')"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Computes the most optimal route between two points based on map geometry,
    live traffic density, and ML-predicted congestion levels.
    """
    try:
        return route_service.optimize_route(origin=origin, destination=destination)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate optimized route: {str(e)}"
        )


@router.get(
    "/alternate",
    response_model=List[AlternateRouteItem],
    summary="Get congestion-aware alternate route recommendations"
)
def get_alternate_routes(
    origin: str = Query(..., description="Starting point coordinates or road identifier"),
    destination: str = Query(..., description="Destination coordinates or road identifier"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns candidate routes ranked by predicted congestion and expected delay.
    Rank 1 is the most recommended alternative route.
    """
    try:
        return route_service.get_alternate_routes(origin=origin, destination=destination)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve alternate routes: {str(e)}"
        )


@router.get(
    "/travel-time",
    response_model=TravelTimeResponse,
    summary="Estimate travel time for a specific route"
)
def get_travel_time(
    route_id: str = Query(..., description="Identifier of the calculated route or road ID"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns estimated travel time, free-flow time, and expected congestion delay.
    Based on 'live+predicted' traffic conditions.
    """
    result = route_service.get_travel_time(route_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route '{route_id}' not found"
        )
    return result


@router.get(
    "/conditions",
    response_model=RoadConditionResponse,
    summary="Get road status, construction, and hazard conditions"
)
def get_route_conditions(
    road_id: str = Query(..., description="Road ID to inspect (e.g. R001)"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns current status (OPEN, CONSTRUCTION, CLOSED, HAZARD) and notes for the given road.
    """
    cond = road_condition_service.get_road_condition(road_id)
    if not cond:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road conditions for '{road_id}' not found"
        )
    return cond


@router.post(
    "/conditions",
    response_model=RoadConditionResponse,
    summary="Update road status, construction, or hazard flags (Operator/Admin only)"
)
def update_road_conditions(
    update_req: RoadConditionUpdateRequest,
    current_user: User = Depends(require_role(["admin", "operator"]))
):
    """
    Updates road conditions (closures, construction, hazards).
    Restricted to operator and admin roles.
    """
    updated = road_condition_service.update_road_condition(
        road_id=update_req.road_id,
        status=update_req.status,
        notes=update_req.notes,
        severity=update_req.severity,
        updated_by=current_user.email
    )
    return updated
