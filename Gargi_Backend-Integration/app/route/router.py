from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.route.conditions import get_road_condition
from app.route.schemas import (
    AlternateRouteResponse,
    RoadConditionResponse,
    RouteResponse,
    TravelTimeResponse,
)
from app.route.service import (
    get_alternate_routes,
    get_travel_time,
    optimize_route,
)

router = APIRouter(
    prefix="/route",
    tags=["Route Analysis"],
)


@router.get(
    "/optimize",
    response_model=RouteResponse,
)
def optimize(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    db: Session = Depends(get_db),
):
    try:
        return optimize_route(
            db=db,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            destination_lat=destination_lat,
            destination_lng=destination_lng,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(f"Route service unavailable: " f"{exc}"),
        )


@router.get(
    "/alternate",
    response_model=list[AlternateRouteResponse],
)
def alternate(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    db: Session = Depends(get_db),
):
    try:
        return get_alternate_routes(
            db=db,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            destination_lat=destination_lat,
            destination_lng=destination_lng,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(f"Route service unavailable: " f"{exc}"),
        )


@router.get(
    "/travel-time",
    response_model=TravelTimeResponse,
)
def travel_time(
    route_id: str,
):
    try:
        return get_travel_time(
            route_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(f"Travel-time calculation " f"failed: {exc}"),
        )


@router.get(
    "/conditions",
    response_model=RoadConditionResponse,
)
def conditions(
    road_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_road_condition(
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
            detail=(f"Road condition lookup failed: " f"{exc}"),
        )
