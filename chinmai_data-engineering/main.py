from fastapi import FastAPI, HTTPException

from traffic_service import (
    get_live_traffic,
    get_road_traffic,
    get_density_summary,
    get_traffic_history,
    get_traffic_aggregate,
    get_road_condition,
    get_hourly_metrics,
    get_daily_metrics
)


app = FastAPI(
    title="Traffic Monitoring Service",
    description=(
        "Traffic monitoring service with congestion history "
        "and Redis-backed live traffic caching."
    ),
    version="2.0.0"
)


@app.get("/")
def root():
    return {
        "service": "Traffic Monitoring Service",
        "status": "running",
        "version": "2.0.0"
    }


@app.get("/api/v1/traffic/live")
def live_traffic():
    return get_live_traffic()


@app.get("/api/v1/traffic/road/{road_id}")
def road_traffic(road_id: str):
    result = get_road_traffic(road_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Road '{road_id}' not found"
        )

    return result


@app.get("/api/v1/traffic/density")
def traffic_density():
    return get_density_summary()

@app.get("/api/v1/traffic/history")
def traffic_history(road_id: str | None = None, start_time: str | None = None, end_time: str | None = None, limit: int = 500):
    if limit < 1 or limit > 5000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 5000")
    return get_traffic_history(road_id, start_time, end_time, limit)


@app.get("/api/v1/traffic/aggregate")
def traffic_aggregate(road_id: str | None = None, start_time: str | None = None, end_time: str | None = None, interval: str = "day"):
    try:
        return get_traffic_aggregate(road_id, start_time, end_time, interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))



@app.get("/api/v1/traffic/road-condition/{road_id}")
def road_condition(road_id: str):
    """Return road-condition information for a specific road."""
    result = get_road_condition(road_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Road '{road_id}' not found"
        )

    return result


@app.get("/api/v1/traffic/metrics/hourly")
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


@app.get("/api/v1/traffic/metrics/daily")
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