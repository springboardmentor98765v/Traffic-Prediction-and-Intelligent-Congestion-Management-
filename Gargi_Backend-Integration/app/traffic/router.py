from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.rbac import require_role
from app.database.connection import get_db
from app.database.models import Road, User
from app.traffic.schemas import (
    TrafficDensityResponse,
    TrafficLiveResponse,
    TrafficRoadResponse,
)
from app.traffic.service import (
    get_latest_traffic,
    get_road,
    get_traffic_history,
)


router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


@router.get(
    "/live",
    response_model=list[TrafficLiveResponse],
)
def live_traffic(
    current_user: User = Depends(
        require_role("admin", "operator", "public")
    ),
    db: Session = Depends(get_db),
):
    roads = (
        db.query(Road)
        .order_by(Road.id)
        .all()
    )

    result = []

    for road in roads:
        record = get_latest_traffic(
            db,
            road.id,
        )

        if not record:
            continue

        updated_at = record.recorded_at

        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(
                tzinfo=timezone.utc
            )

        result.append(
            {
                "road_id": road.id,
                "vehicle_count": record.vehicle_count,
                "density": record.density,
                "congestion_level": record.congestion_level,
                "updated_at": updated_at,
            }
        )

    return result


@router.get(
    "/road/{road_id}",
    response_model=TrafficRoadResponse,
)
def road_traffic(
    road_id: int,
    current_user: User = Depends(
        require_role("admin", "operator", "public")
    ),
    db: Session = Depends(get_db),
):
    road = get_road(
        db,
        road_id,
    )

    if not road:
        raise HTTPException(
            status_code=404,
            detail="Road not found",
        )

    records = get_traffic_history(
        db,
        road_id,
    )

    history = []

    for record in records:
        timestamp = record.recorded_at

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        history.append(
            {
                "timestamp": timestamp,
                "vehicle_count": record.vehicle_count,
                "density": record.density,
                "congestion_level": record.congestion_level,
            }
        )

    latest = records[0] if records else None

    return {
        "road_id": road.id,
        "name": road.name,
        "congestion_level": (
            latest.congestion_level
            if latest
            else "UNKNOWN"
        ),
        "history": history,
    }


@router.get(
    "/density",
    response_model=list[TrafficDensityResponse],
)
def traffic_density(
    current_user: User = Depends(
        require_role("admin", "operator", "public")
    ),
    db: Session = Depends(get_db),
):
    roads = (
        db.query(Road)
        .order_by(Road.id)
        .all()
    )

    result = []

    for road in roads:
        record = get_latest_traffic(
            db,
            road.id,
        )

        if not record:
            continue

        result.append(
            {
                "road_id": road.id,
                "density": record.density,
                "congestion_level": record.congestion_level,
            }
        )

    return result


@router.post("/record")
def create_traffic_record_endpoint(
    road_id: int,
    vehicle_count: int,
    density: float,
    congestion_level: str,
    current_user: User = Depends(
        require_role("admin", "operator")
    ),
    db: Session = Depends(get_db),
):
    from app.traffic.service import create_traffic_record

    road = get_road(
        db,
        road_id,
    )

    if not road:
        raise HTTPException(
            status_code=404,
            detail="Road not found",
        )

    record = create_traffic_record(
        db,
        road_id,
        vehicle_count,
        density,
        congestion_level,
    )

    return {
        "id": record.id,
        "road_id": record.road_id,
        "vehicle_count": record.vehicle_count,
        "density": record.density,
        "congestion_level": record.congestion_level,
    }
