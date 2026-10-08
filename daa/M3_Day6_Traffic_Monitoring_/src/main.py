import os
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response


from traffic_service import (
    get_live_traffic,
    get_road_traffic,
    get_density_summary,
    get_traffic_history,
    get_traffic_aggregate,
    get_road_condition,
    get_hourly_metrics,
    get_daily_metrics,
)


from analytics_service import get_traffic_trends


from heatmap_service import get_traffic_heatmap


from report_service import generate_historical_report


from analytics_cache import get_cached, set_cached


from database import road_exists

# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Traffic Monitoring Service",
    description=(
        "Traffic monitoring service with congestion history "
        "and Redis-backed live traffic caching."
    ),
    version="2.0.0",
)


# =========================================================
# CORS
# M3 DAY 6 - DEF-M3-014
# =========================================================

# CORS: production sets CORS_ALLOWED_ORIGINS to the hosted frontend (comma-separated,
# DEF-M4-006); unset means "*" so local development keeps working.
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================


@app.get("/")
def root():
    return {"service": "Traffic Monitoring Service", "status": "running", "version": "2.0.0"}


# =========================================================
# M1 - LIVE TRAFFIC
# =========================================================


@app.get("/api/v1/traffic/live")
def live_traffic():
    return get_live_traffic()


# =========================================================
# M1 - ROAD TRAFFIC
# =========================================================


@app.get("/api/v1/traffic/road/{road_id}")
def road_traffic(road_id: str):

    result = get_road_traffic(road_id)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Road '{road_id}' not found")

    return result


# =========================================================
# M1 - DENSITY
# =========================================================


@app.get("/api/v1/traffic/density")
def traffic_density():
    return get_density_summary()


# =========================================================
# M2 DAY 3 - HISTORICAL TRAFFIC
#
# IMPORTANT:
# Keep the original service signature:
#
# get_traffic_history(
#     road_id,
#     start_time,
#     end_time,
#     limit
# )
#
# This fixes the old M2 regression tests.
# =========================================================


@app.get("/api/v1/traffic/history")
def traffic_history(
    road_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    limit: int = 500,
):

    if limit < 1 or limit > 5000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 5000")

    return get_traffic_history(road_id, start_time, end_time, limit)


# =========================================================
# M2 DAY 3 - AGGREGATE
#
# Keep the original service signature.
# =========================================================


@app.get("/api/v1/traffic/aggregate")
def traffic_aggregate(
    road_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    interval: str = "day",
):

    try:

        return get_traffic_aggregate(road_id, start_time, end_time, interval)

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc))


# =========================================================
# M2 DAY 4 - ROAD CONDITION
# =========================================================


@app.get("/api/v1/traffic/road-condition/{road_id}")
def road_condition(road_id: str):

    result = get_road_condition(road_id)

    if result is None:

        raise HTTPException(status_code=404, detail=f"Road '{road_id}' not found")

    return result


# =========================================================
# M2 DAY 5 - HOURLY METRICS
# =========================================================


@app.get("/api/v1/traffic/metrics/hourly")
def hourly_metrics(
    road_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    limit: int = 500,
):

    if limit < 1 or limit > 5000:

        raise HTTPException(status_code=400, detail="limit must be between 1 and 5000")

    return get_hourly_metrics(road_id, start_time, end_time, limit)


# =========================================================
# M2 DAY 5 - DAILY METRICS
# =========================================================


@app.get("/api/v1/traffic/metrics/daily")
def daily_metrics(
    road_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 500,
):

    if limit < 1 or limit > 5000:

        raise HTTPException(status_code=400, detail="limit must be between 1 and 5000")

    return get_daily_metrics(road_id, start_date, end_date, limit)


# =========================================================
# COMMON M3 DATE VALIDATION
# =========================================================


def validate_date_range(start_date: date | None, end_date: date | None):

    if start_date and end_date and start_date > end_date:

        raise HTTPException(
            status_code=400, detail=("start_date must be less than " "or equal to end_date")
        )


# =========================================================
# M3 DAY 3 - ANALYTICS TRENDS
#
# DEF-M3-009:
# FastAPI date validation prevents malformed dates
# from reaching the service.
#
# DEF-M3-011:
# Unknown road -> 404.
#
# =========================================================


@app.get("/analytics/trends")
def analytics_trends(road_id: str, start_date: date | None = None, end_date: date | None = None):

    validate_date_range(start_date, end_date)

    # -----------------------------------------------------
    # ROAD EXISTENCE
    # -----------------------------------------------------

    if not road_exists(road_id):

        raise HTTPException(status_code=404, detail=f"Road '{road_id}' not found")

    # -----------------------------------------------------
    # Convert date objects to ISO strings
    # -----------------------------------------------------

    start_date_value = start_date.isoformat() if start_date else None

    end_date_value = end_date.isoformat() if end_date else None

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    cache_values = {
        "road_id": road_id,
        "start_date": start_date_value,
        "end_date": end_date_value,
    }

    cached = get_cached("trends", cache_values)

    if cached is not None:
        return cached

    # -----------------------------------------------------
    # SERVICE
    # -----------------------------------------------------

    try:

        result = get_traffic_trends(
            road_id=road_id, start_date=start_date_value, end_date=end_date_value
        )

        set_cached("trends", cache_values, result)

        return result

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc))


# =========================================================
# M3 DAY 4 - HEATMAP
#
# DEF-M3-009:
# Malformed dates -> FastAPI 422 instead of 500.
#
# DEF-M3-011:
# Inverted date range -> 400.
#
# =========================================================


@app.get("/analytics/heatmap")
def analytics_heatmap(
    start_date: date | None = None, end_date: date | None = None, time_bucket: str = "hour"
):

    validate_date_range(start_date, end_date)

    # -----------------------------------------------------
    # Convert date objects to ISO strings
    # -----------------------------------------------------

    start_date_value = start_date.isoformat() if start_date else None

    end_date_value = end_date.isoformat() if end_date else None

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    cache_values = {
        "start_date": start_date_value,
        "end_date": end_date_value,
        "time_bucket": time_bucket,
    }

    cached = get_cached("heatmap", cache_values)

    if cached is not None:
        return cached

    # -----------------------------------------------------
    # SERVICE
    # -----------------------------------------------------

    try:

        result = get_traffic_heatmap(
            start_date=start_date_value, end_date=end_date_value, time_bucket=time_bucket
        )

        set_cached("heatmap", cache_values, result)

        return result

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc))


# =========================================================
# M3 DAY 5 - HISTORICAL REPORT
#
# DEF-M3-009:
# Malformed dates -> FastAPI validation.
#
# DEF-M3-010:
# Report service uses Asia/Kolkata date semantics.
#
# DEF-M3-011:
# Unknown road -> 404.
#
# =========================================================


@app.get("/analytics/reports")
def analytics_report(
    road_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 10000,
):

    validate_date_range(start_date, end_date)

    # -----------------------------------------------------
    # ROAD EXISTENCE
    # -----------------------------------------------------

    if road_id:

        if not road_exists(road_id):

            raise HTTPException(status_code=404, detail=f"Road '{road_id}' not found")

    # -----------------------------------------------------
    # Convert date objects to ISO strings
    # -----------------------------------------------------

    start_date_value = start_date.isoformat() if start_date else None

    end_date_value = end_date.isoformat() if end_date else None

    # -----------------------------------------------------
    # GENERATE REPORT
    # -----------------------------------------------------

    try:

        csv_text, row_count = generate_historical_report(
            road_id=road_id,
            start_date=start_date_value,
            end_date=end_date_value,
            limit=limit,
        )

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc))

    # -----------------------------------------------------
    # FILE NAME
    # -----------------------------------------------------

    filename = "traffic_historical_report.csv"

    if road_id:

        filename = f"traffic_historical_report_{road_id}.csv"

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={
            "Content-Disposition": (f'attachment; filename="{filename}"'),
            "X-Report-Row-Count": str(row_count),
        },
    )
