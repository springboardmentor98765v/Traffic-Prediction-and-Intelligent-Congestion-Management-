from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.rbac import require_role
from app.database.connection import get_db
from app.database.models import Road, TrafficRecord
from app.traffic.schemas import (
    TrafficAggregateItem,
    TrafficHistoryItem,
)

router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


@router.get("/nodes")
def get_traffic_nodes(
    db: Session = Depends(get_db),
):
    roads = db.query(Road).order_by(Road.id).all()

    coordinates = {
        1: {
            "lat": 13.0569,
            "lng": 80.2425,
        },
        2: {
            "lat": 13.0524,
            "lng": 80.2508,
        },
        3: {
            "lat": 12.9941,
            "lng": 80.1709,
        },
    }

    nodes = []

    for road in roads:
        record = (
            db.query(TrafficRecord)
            .filter(TrafficRecord.road_id == road.id)
            .order_by(TrafficRecord.recorded_at.desc())
            .first()
        )

        if not record:
            continue

        location = coordinates.get(
            road.id,
            {
                "lat": 13.0827,
                "lng": 80.2707,
            },
        )

        if record.congestion_level == "HIGH":
            status = "Congested"
        elif record.congestion_level == "MEDIUM":
            status = "Moderate"
        else:
            status = "Clear"

        if record.density >= 0.80:
            density = "High"
        elif record.density >= 0.50:
            density = "Medium"
        else:
            density = "Low"

        nodes.append(
            {
                "id": str(road.id),
                "name": road.name,
                "coords": f"{location['lat']}, {location['lng']}",
                "lat": location["lat"],
                "lng": location["lng"],
                "status": status,
                "count": record.vehicle_count,
                "density": density,
            }
        )

    return nodes


@router.get("/history", response_model=list[TrafficHistoryItem])
def get_traffic_history(
    road_id: int,
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db),
):
    if start >= end:
        raise HTTPException(
            status_code=400,
            detail="start must be earlier than end",
        )

    records = (
        db.query(TrafficRecord)
        .filter(
            TrafficRecord.road_id == road_id,
            TrafficRecord.recorded_at >= start,
            TrafficRecord.recorded_at <= end,
        )
        .order_by(TrafficRecord.recorded_at)
        .all()
    )

    return [
        {
            "road_id": record.road_id,
            "timestamp": record.recorded_at,
            "vehicle_count": record.vehicle_count,
            "density": record.density,
            "congestion_level": record.congestion_level,
        }
        for record in records
    ]


@router.get(
    "/aggregate",
    response_model=list[TrafficAggregateItem],
)
def get_traffic_aggregate(
    road_id: int,
    granularity: str,
    db: Session = Depends(get_db),
):
    if granularity not in ["hour", "day"]:
        raise HTTPException(
            status_code=400,
            detail="granularity must be hour or day",
        )

    if granularity == "hour":
        period_expression = func.date_trunc(
            "hour",
            TrafficRecord.recorded_at,
        )
    else:
        period_expression = func.date_trunc(
            "day",
            TrafficRecord.recorded_at,
        )

    results = (
        db.query(
            TrafficRecord.road_id,
            period_expression.label("period"),
            func.avg(TrafficRecord.vehicle_count).label(
                "average_vehicle_count"
            ),
            func.avg(TrafficRecord.density).label(
                "average_density"
            ),
        )
        .filter(TrafficRecord.road_id == road_id)
        .group_by(
            TrafficRecord.road_id,
            period_expression,
        )
        .order_by(period_expression)
        .all()
    )

    return [
        {
            "road_id": result.road_id,
            "period": result.period.isoformat(),
            "average_vehicle_count": round(
                float(result.average_vehicle_count),
                2,
            ),
            "average_density": round(
                float(result.average_density),
                2,
            ),
        }
        for result in results
    ]


@router.post("/record")
def record_traffic(
    road_id: int,
    vehicle_count: int,
    density: float,
    congestion_level: str,
    current_user=Depends(
        require_role("admin", "operator")
    ),
    db: Session = Depends(get_db),
):
    record = TrafficRecord(
        road_id=road_id,
        vehicle_count=vehicle_count,
        density=density,
        congestion_level=congestion_level,
        recorded_at=datetime.now(timezone.utc),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Traffic record created",
        "record_id": record.id,
    }