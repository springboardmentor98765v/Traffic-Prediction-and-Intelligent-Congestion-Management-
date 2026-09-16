"""
TrafficVision AI — Traffic Monitoring Service (Day 3)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Exposes the traffic_readings data (that ingest_live_data.py has been
    writing since Day 2) as REST API endpoints, matching the frozen
    interface contract from the SRS (Section 7.2):

        GET /api/v1/traffic/live
        GET /api/v1/traffic/road/{road_id}
        GET /api/v1/traffic/density

Consumed by:
    - Intern 1 (registers these routes behind the API Gateway)
    - Intern 4 (frontend dashboard calls these directly for now)
    - Intern 5 (writes automated tests against these endpoints)

Requirements:
    pip install fastapi uvicorn psycopg2-binary

Run:
    uvicorn main:app --reload

Then open in browser:
    http://127.0.0.1:8000/docs   <- free interactive Swagger UI (built into FastAPI)
"""

from datetime import datetime
from typing import List, Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException

from redis_cache import cache_get, cache_set
from congestion_tracking import calculate_road_utilization, build_congestion_state_history

# ---------------------------------------------------------
# CONFIG — same DB, same password you used in ingest_live_data.py
# ---------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "kitty@2211",   # <-- put your actual postgres password
}

app = FastAPI(
    title="TrafficVision AI — Traffic Monitoring Service",
    description="Milestone 1, Day 3 — Intern 2 (Data Engineering & Traffic Monitoring)",
    version="0.1.0",
)


def get_connection():
    """Open a fresh DB connection for this request."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")


# ---------------------------------------------------------
# 1. GET /api/v1/traffic/live
#    -> [ { road_id, vehicle_count, density, congestion_level, updated_at } ]
# ---------------------------------------------------------
@app.get("/api/v1/traffic/live")
def get_live_traffic():
    """
    Returns the MOST RECENT reading for every road — this is what the
    dashboard polls to show live status across the whole city.

    Day 4 addition: checks Redis first. If cached data exists and hasn't
    expired (5 second TTL), it's returned instantly without touching the
    database at all — this is what keeps repeated polling fast.
    """
    cache_key = "traffic:live"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (road_id)
                    road_id, vehicle_count, density, congestion_level, recorded_at AS updated_at
                FROM traffic_readings
                ORDER BY road_id, recorded_at DESC;
                """
            )
            rows = cur.fetchall()
        cache_set(cache_key, rows, ttl=5)
        return rows
    finally:
        conn.close()


# ---------------------------------------------------------
# 2. GET /api/v1/traffic/road/{road_id}
#    -> { road_id, name, congestion_level, history[] }
# ---------------------------------------------------------
@app.get("/api/v1/traffic/road/{road_id}")
def get_road_detail(road_id: int, history_limit: int = 20):
    """
    Returns details for ONE specific road, including its most recent
    congestion level and a short history of past readings.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Confirm the road exists and get its name
            cur.execute("SELECT road_id, road_name FROM roads WHERE road_id = %s;", (road_id,))
            road = cur.fetchone()
            if not road:
                raise HTTPException(status_code=404, detail=f"road_id {road_id} not found")

            # Latest congestion level for this road
            cur.execute(
                """
                SELECT congestion_level FROM traffic_readings
                WHERE road_id = %s ORDER BY recorded_at DESC LIMIT 1;
                """,
                (road_id,),
            )
            latest = cur.fetchone()
            current_level = latest["congestion_level"] if latest else "UNKNOWN"

            # Recent history for this road
            cur.execute(
                """
                SELECT vehicle_count, density, congestion_level, recorded_at
                FROM traffic_readings
                WHERE road_id = %s
                ORDER BY recorded_at DESC
                LIMIT %s;
                """,
                (road_id, history_limit),
            )
            history = cur.fetchall()

        return {
            "road_id": road["road_id"],
            "name": road["road_name"],
            "congestion_level": current_level,
            "history": history,
        }
    finally:
        conn.close()


# ---------------------------------------------------------
# NEW: GET /api/v1/traffic/road/by-name/{road_name}
#    -> same shape as /road/{road_id}, but searched by name instead of ID
# ---------------------------------------------------------
@app.get("/api/v1/traffic/road/by-name/{road_name}")
def get_road_by_name(road_name: str, history_limit: int = 20):
    """
    Same as get_road_detail(), but lets you type a road NAME (like
    'Anna Salai') instead of needing to know its numeric road_id.
    Case-insensitive and matches partial names too, e.g. 'anna' will
    find 'Anna Salai'.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # ILIKE = case-insensitive match; % wildcards allow partial matches
            cur.execute(
                "SELECT road_id, road_name FROM roads WHERE road_name ILIKE %s LIMIT 1;",
                (f"%{road_name}%",),
            )
            road = cur.fetchone()
            if not road:
                raise HTTPException(status_code=404, detail=f"No road found matching '{road_name}'")

            road_id = road["road_id"]

            cur.execute(
                """
                SELECT congestion_level FROM traffic_readings
                WHERE road_id = %s ORDER BY recorded_at DESC LIMIT 1;
                """,
                (road_id,),
            )
            latest = cur.fetchone()
            current_level = latest["congestion_level"] if latest else "UNKNOWN"

            cur.execute(
                """
                SELECT vehicle_count, density, congestion_level, recorded_at
                FROM traffic_readings
                WHERE road_id = %s
                ORDER BY recorded_at DESC
                LIMIT %s;
                """,
                (road_id, history_limit),
            )
            history = cur.fetchall()

        return {
            "road_id": road["road_id"],
            "name": road["road_name"],
            "congestion_level": current_level,
            "history": history,
        }
    finally:
        conn.close()


# ---------------------------------------------------------
# NEW (Day 4): GET /api/v1/traffic/road/{road_id}/tracking
#    -> road utilization % + grouped congestion state history
# ---------------------------------------------------------
@app.get("/api/v1/traffic/road/{road_id}/tracking")
def get_road_tracking(road_id: int, history_limit: int = 30):
    """
    Day 4 addition. Two things the SRS asks for:
      1. Road utilization — how full the road is right now, relative to
         a rough per-lane capacity.
      2. Congestion state history — instead of raw individual readings,
         grouped segments showing when the road moved between states
         (e.g. "LOW from 10:00 to 10:15, then MODERATE from 10:15...").
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT road_id, road_name, lanes FROM roads WHERE road_id = %s;", (road_id,))
            road = cur.fetchone()
            if not road:
                raise HTTPException(status_code=404, detail=f"road_id {road_id} not found")

            cur.execute(
                """
                SELECT vehicle_count, congestion_level, recorded_at
                FROM traffic_readings
                WHERE road_id = %s
                ORDER BY recorded_at ASC
                LIMIT %s;
                """,
                (road_id, history_limit),
            )
            readings = cur.fetchall()

        current_vehicle_count = readings[-1]["vehicle_count"] if readings else 0
        utilization = calculate_road_utilization(current_vehicle_count, road["lanes"])
        state_history = build_congestion_state_history(readings)

        return {
            "road_id": road["road_id"],
            "name": road["road_name"],
            "current_utilization_percent": utilization,
            "congestion_state_history": state_history,
        }
    finally:
        conn.close()


# ---------------------------------------------------------
# 3. GET /api/v1/traffic/density
#    -> aggregated density metrics for dashboard KPIs
# ---------------------------------------------------------
@app.get("/api/v1/traffic/density")
def get_density_summary():
    """
    Returns city-wide aggregated stats — useful for dashboard KPI cards
    like "average density across all roads" or "how many roads are HIGH/SEVERE".
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Average density across the latest reading per road
            cur.execute(
                """
                WITH latest AS (
                    SELECT DISTINCT ON (road_id) road_id, density, congestion_level
                    FROM traffic_readings
                    ORDER BY road_id, recorded_at DESC
                )
                SELECT
                    ROUND(AVG(density), 2) AS avg_density,
                    COUNT(*) AS total_roads_monitored,
                    COUNT(*) FILTER (WHERE congestion_level = 'LOW') AS low_count,
                    COUNT(*) FILTER (WHERE congestion_level = 'MODERATE') AS moderate_count,
                    COUNT(*) FILTER (WHERE congestion_level = 'HIGH') AS high_count,
                    COUNT(*) FILTER (WHERE congestion_level = 'SEVERE') AS severe_count
                FROM latest;
                """
            )
            summary = cur.fetchone()
        return summary
    finally:
        conn.close()


# ---------------------------------------------------------
# Simple root route — just to confirm the service is alive
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"service": "Traffic Monitoring Service", "status": "running"}
