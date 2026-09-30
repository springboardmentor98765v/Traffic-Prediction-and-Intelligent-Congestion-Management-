from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any
from datetime import datetime
from app.services.traffic_service import (
    get_live_traffic,
    get_road_traffic,
    get_density_summary,
    get_traffic_history,
    get_traffic_aggregate,
    get_road_condition,
    get_hourly_metrics,
    get_daily_metrics
)

router = APIRouter(
    tags=["Traffic Monitoring"]
)

# Mock in-memory data feed based on Intern 2's dataset
SAMPLE_TRAFFIC_DATA = [
    {
        "road_id": "R001",
        "road_name": "Main Expressway",
        "vehicle_count": 28,
        "density": 5.6,
        "congestion_level": "Low",
        "updated_at": "2026-08-26T22:00:00"
    },
    {
        "road_id": "R002",
        "road_name": "Central Avenue",
        "vehicle_count": 27,
        "density": 6.75,
        "congestion_level": "Low",
        "updated_at": "2026-08-26T22:00:00"
    },
    {
        "road_id": "R003",
        "road_name": "West Ring Road",
        "vehicle_count": 26,
        "density": 7.43,
        "congestion_level": "Low",
        "updated_at": "2026-08-26T22:00:00"
    },
    {
        "road_id": "R004",
        "road_name": "North Boulevard",
        "vehicle_count": 1,
        "density": 0.22,
        "congestion_level": "Low",
        "updated_at": "2026-08-26T22:00:00"
    },
    {
        "road_id": "R005",
        "road_name": "Industrial Highway",
        "vehicle_count": 34,
        "density": 11.33,
        "congestion_level": "Medium",
        "updated_at": "2026-08-26T22:00:00"
    },
    {
        "road_id": "R006",
        "road_name": "Airport Road",
        "vehicle_count": 55,
        "density": 22.4,
        "congestion_level": "High",
        "updated_at": "2026-08-26T22:00:00"
    }
]


@router.get("/live", response_model=List[Dict[str, Any]])
def live_traffic_endpoint():
    """Returns real-time vehicle count and congestion status for all monitored roads."""
    # NOTE: the route handler used to be named get_live_traffic(), the exact same
    # name as the real, DB-backed function imported from traffic_service above —
    # that rebound the module-level name and permanently shadowed the import,
    # so this endpoint always returned the hardcoded SAMPLE_TRAFFIC_DATA
    # regardless of what was in the database. Renamed the handler and now
    # actually calls the imported service function.
    return get_live_traffic()


@router.get("/road/{road_id}", response_model=Dict[str, Any])
def road_traffic_endpoint(road_id: str):
    """Returns real-time traffic details for a specific road ID."""
    result = get_road_traffic(road_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Road segment not found")
    return result


@router.get("/density", response_model=Dict[str, Any])
def traffic_density_endpoint():
    """Aggregated density metrics for dashboard KPI cards."""
    return get_density_summary()


@router.get("/history")
def traffic_history(road_id: str | None = None, start_time: str | None = None, end_time: str | None = None, limit: int = 500):
    if limit < 1 or limit > 5000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 5000")
    return get_traffic_history(road_id, start_time, end_time, limit)


@router.get("/aggregate")
def traffic_aggregate(road_id: str | None = None, start_time: str | None = None, end_time: str | None = None, interval: str = "day"):
    try:
        return get_traffic_aggregate(road_id, start_time, end_time, interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/road-condition/{road_id}")
def road_condition(road_id: str):
    """Return road-condition information for a specific road."""
    result = get_road_condition(road_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Road '{road_id}' not found"
        )

    return result


@router.get("/metrics/hourly")
def hourly_metrics(
    road_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    limit: int = 500
):
    if limit < 1 or limit > 5000:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 5000"
        )

    return get_hourly_metrics(
        road_id,
        start_time,
        end_time,
        limit
    )


@router.get("/metrics/daily")
def daily_metrics(
    road_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 500
):
    if limit < 1 or limit > 5000:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 5000"
        )

    return get_daily_metrics(
        road_id,
        start_date,
        end_date,
        limit
    )