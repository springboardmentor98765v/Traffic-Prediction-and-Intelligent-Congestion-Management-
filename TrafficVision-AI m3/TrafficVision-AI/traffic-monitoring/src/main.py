from fastapi import FastAPI, HTTPException

from route_ranking import rank_routes

from traffic_service import (
    get_live_traffic,
    get_road_traffic,
    get_density_summary,
)

from predict_service import (
    get_congestion_prediction,
    get_peak_hour_prediction,
    get_delay_prediction,
)


app = FastAPI(
    title="Traffic Monitoring Service",
    description=(
        "Traffic monitoring service with congestion history "
        "and Redis-backed live traffic caching."
    ),
    version="2.0.0",
)


@app.get("/")
def root():
    return {
        "service": "Traffic Monitoring Service",
        "status": "running",
        "version": "2.0.0",
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
            detail=f"Road '{road_id}' not found",
        )

    return result


@app.get("/api/v1/traffic/density")
def traffic_density():
    return get_density_summary()


@app.get("/api/v1/predict/congestion")
def congestion_prediction(road_id: str):
    result = get_congestion_prediction(road_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No traffic reading found for road '{road_id}'",
        )

    return result


@app.get("/api/v1/predict/peak-hours")
def peak_hour_prediction(road_id: str):
    result = get_peak_hour_prediction(road_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No traffic reading found for road '{road_id}'",
        )

    return result


@app.get("/api/v1/predict/delay")
def delay_prediction(road_id: str):
    result = get_delay_prediction(road_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No traffic reading found for road '{road_id}'",
        )

    return result


@app.post("/api/v1/routes/rank")
def route_ranking(routes: list[dict]):
    return {
        "ranked_routes": rank_routes(routes),
        "generated_by": "route-ranking-v1",
    }