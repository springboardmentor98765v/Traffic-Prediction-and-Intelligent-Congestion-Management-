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

from datetime import datetime, timedelta
from typing import List, Optional
import csv
import io
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

from redis_cache import cache_get, cache_set
from congestion_tracking import calculate_road_utilization, build_congestion_state_history
from analytics_helpers import build_heatmap_grid

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
# NEW (Milestone 2, Day 3): GET /api/v1/traffic/history
#    -> [ { road_id, timestamp, vehicle_count, density, congestion_level } ]
#    Consumed by: Intern 3 (feature engineering for model training)
# ---------------------------------------------------------
@app.get("/api/v1/traffic/history")
def get_traffic_history(road_id: int, start: str, end: str, limit: int = 5000):
    """
    Returns raw historical readings for a road within a time range.

    Query params (per the M2 interface contract):
        road_id — required
        start   — ISO timestamp, e.g. 2026-09-01T00:00:00
        end     — ISO timestamp, e.g. 2026-09-07T23:59:59
        limit   — max rows to return (default 5000, capped at 20000).
                  DEFECT FIX (Day 7): this endpoint used to have NO cap
                  at all — a wide date range on a road with a lot of
                  accumulated data (live ingestion running for days,
                  on top of the historical backfill) could return
                  40,000+ rows in a single response. Turning that many
                  rows into JSON is slow enough to time out callers and
                  puts unnecessary load on the API for a single request.
                  A sane default cap protects against this while still
                  letting a caller raise it explicitly if they really
                  need more (up to a hard ceiling of 20,000).

    This is what Intern 3's feature engineering pulls from — the same
    historical data generated on Day 2, now exposed through a proper API
    instead of requiring direct database access.
    """
    try:
        start_ts = datetime.fromisoformat(start)
        end_ts = datetime.fromisoformat(end)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="start and end must be ISO format timestamps, e.g. 2026-09-01T00:00:00",
        )

    if start_ts >= end_ts:
        raise HTTPException(status_code=400, detail="start must be earlier than end")

    limit = max(1, min(limit, 20000))  # clamp between 1 and 20,000

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT 1 FROM roads WHERE road_id = %s;", (road_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail=f"road_id {road_id} not found")

            # Get the TRUE total count first, so callers know if the
            # response was truncated by the limit — without this, a
            # caller getting back exactly 5000 rows would have no way
            # to know whether that's everything or just the first page.
            cur.execute(
                """
                SELECT COUNT(*) AS total FROM traffic_readings
                WHERE road_id = %s AND recorded_at BETWEEN %s AND %s;
                """,
                (road_id, start_ts, end_ts),
            )
            total_matching = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT road_id, recorded_at AS timestamp, vehicle_count, density, congestion_level
                FROM traffic_readings
                WHERE road_id = %s AND recorded_at BETWEEN %s AND %s
                ORDER BY recorded_at ASC
                LIMIT %s;
                """,
                (road_id, start_ts, end_ts, limit),
            )
            rows = cur.fetchall()
        return {
            "road_id": road_id,
            "total_matching_readings": total_matching,
            "returned_count": len(rows),
            "truncated": total_matching > len(rows),
            "readings": rows,
        }
    finally:
        conn.close()


# ---------------------------------------------------------
# NEW (Milestone 2, Day 3): GET /api/v1/traffic/aggregate
#    -> rolled-up averages for trend analysis and model features
#    Consumed by: Intern 3 (feature engineering for model training)
# ---------------------------------------------------------
@app.get("/api/v1/traffic/aggregate")
def get_traffic_aggregate(road_id: int, granularity: str = "hour"):
    """
    Returns rolled-up averages (density, vehicle_count) bucketed by
    hour or day — much more useful for spotting trends than looking
    at individual 5-minute readings one by one.
    """
    # Defect fix (Day 6): normalize case so "Hour", "HOUR", "hour" all
    # work the same way, instead of only accepting the exact lowercase
    # string. A real user or another service calling this API shouldn't
    # get a confusing 400 error just because of capitalization.
    granularity = granularity.lower().strip()

    if granularity not in ("hour", "day"):
        raise HTTPException(status_code=400, detail="granularity must be 'hour' or 'day'")

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT 1 FROM roads WHERE road_id = %s;", (road_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail=f"road_id {road_id} not found")

            # date_trunc buckets timestamps into the requested granularity
            # (e.g. every reading in the same hour gets grouped together)
            cur.execute(
                f"""
                SELECT
                    date_trunc('{granularity}', recorded_at) AS bucket,
                    ROUND(AVG(density), 2) AS avg_density,
                    ROUND(AVG(vehicle_count), 0) AS avg_vehicle_count,
                    COUNT(*) AS reading_count
                FROM traffic_readings
                WHERE road_id = %s
                GROUP BY bucket
                ORDER BY bucket ASC;
                """,
                (road_id,),
            )
            rows = cur.fetchall()
        return {"road_id": road_id, "granularity": granularity, "buckets": rows}
    finally:
        conn.close()


# ---------------------------------------------------------
# NEW (Milestone 2, Day 5): GET /api/v1/traffic/features/{road_id}
#    -> feature-engineering-friendly summary for Intern 3's model training
#    Uses the traffic_daily_summary materialized view for speed.
# ---------------------------------------------------------
@app.get("/api/v1/traffic/features/{road_id}")
def get_traffic_features(road_id: int):
    """
    Returns pre-computed features specifically shaped for model
    training, not just raw data:
      - avg_density_by_hour: average density for each hour 0-23
        (captures the rush-hour pattern as a reusable feature)
      - avg_density_by_weekday: average density for each day 0-6
        (captures the weekday/weekend pattern from Day 2's generator)
      - peak_hours: the top 3 hours with highest average density
      - overall_avg_density / overall_max_density: quick summary stats

    This saves Intern 3 from re-deriving these patterns manually from
    raw readings — the patterns are already known (we built them into
    the Day 2 generator), so exposing them directly as features is more
    useful than making the AI/ML side re-discover them from scratch.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT 1 FROM roads WHERE road_id = %s;", (road_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail=f"road_id {road_id} not found")

            # Average density per hour of day (0-23)
            cur.execute(
                """
                SELECT EXTRACT(HOUR FROM recorded_at)::int AS hour,
                       ROUND(AVG(density), 2) AS avg_density
                FROM traffic_readings
                WHERE road_id = %s
                GROUP BY hour
                ORDER BY hour;
                """,
                (road_id,),
            )
            by_hour = cur.fetchall()

            # Average density per day of week (0=Sunday ... 6=Saturday)
            cur.execute(
                """
                SELECT EXTRACT(DOW FROM recorded_at)::int AS weekday,
                       ROUND(AVG(density), 2) AS avg_density
                FROM traffic_readings
                WHERE road_id = %s
                GROUP BY weekday
                ORDER BY weekday;
                """,
                (road_id,),
            )
            by_weekday = cur.fetchall()

            # Top 3 peak hours by average density
            peak_hours = sorted(by_hour, key=lambda r: r["avg_density"], reverse=True)[:3]

            # Overall summary stats
            cur.execute(
                """
                SELECT ROUND(AVG(density), 2) AS overall_avg_density,
                       ROUND(MAX(density), 2) AS overall_max_density,
                       COUNT(*) AS total_readings
                FROM traffic_readings
                WHERE road_id = %s;
                """,
                (road_id,),
            )
            overall = cur.fetchone()

        return {
            "road_id": road_id,
            "avg_density_by_hour": by_hour,
            "avg_density_by_weekday": by_weekday,
            "peak_hours": [{"hour": p["hour"], "avg_density": p["avg_density"]} for p in peak_hours],
            **overall,
        }
    finally:
        conn.close()


# ---------------------------------------------------------
# NEW (Milestone 3, Day 3): GET /api/v1/analytics/trends
#    -> { road_id, points: [ { period, avg_congestion } ] }
#    Consumed by: Intern 3 (recommendation input), Intern 4 (trend
#    charts), Intern 5 (test target)
#
#    Design note (per Day 1 planning): this REUSES the hour/weekday
#    aggregation logic already built for /traffic/features (M2 Day 5),
#    reshaped into the Milestone 3 Analytics contract's response
#    format. Not new engineering — a deliberate re-shaping of existing
#    logic, per the Day 1 plan.
# ---------------------------------------------------------
@app.get("/api/v1/analytics/trends")
def get_analytics_trends(road_id: int, range_: str = Query("day", alias="range")):
    """
    Returns a congestion pattern for one road, shaped for the
    Analytics contract:
        range=day  -> 24 points, one per hour of day (0-23)
        range=week -> 7 points, one per day of week (0=Sunday..6=Saturday)

    This answers "what does a typical day/week look like for this
    road" — e.g. "this road is usually busy every weekday at 6pm" —
    which is exactly the trend pattern description in the SRS.

    NOTE: internally named range_ (not range) since "range" is a
    Python built-in — kept consistent with the same fix applied to
    the heatmap endpoint on Day 4, using Query's alias to keep the
    URL parameter itself as ?range=... per the SRS contract.
    """
    range_ = range_.lower().strip()  # same defensive normalization as the Day 6 granularity fix
    if range_ not in ("day", "week"):
        raise HTTPException(status_code=400, detail="range must be 'day' or 'week'")

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT 1 FROM roads WHERE road_id = %s;", (road_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail=f"road_id {road_id} not found")

            if range_ == "day":
                cur.execute(
                    """
                    SELECT EXTRACT(HOUR FROM recorded_at)::int AS period,
                           ROUND(AVG(density), 2) AS avg_congestion
                    FROM traffic_readings
                    WHERE road_id = %s
                    GROUP BY period
                    ORDER BY period;
                    """,
                    (road_id,),
                )
            else:  # range_ == "week"
                cur.execute(
                    """
                    SELECT EXTRACT(DOW FROM recorded_at)::int AS period,
                           ROUND(AVG(density), 2) AS avg_congestion
                    FROM traffic_readings
                    WHERE road_id = %s
                    GROUP BY period
                    ORDER BY period;
                    """,
                    (road_id,),
                )
            points = cur.fetchall()

        return {"road_id": road_id, "range": range_, "points": points}
    finally:
        conn.close()


# ---------------------------------------------------------
# NEW (Milestone 3, Day 4): GET /api/v1/analytics/heatmap
#    -> { roads: [...], time_buckets: [...], values: [][] }
#    Consumed by: Intern 4 (heatmap visualization)
#
#    Design note: this is the genuinely NEW piece flagged on Day 1 —
#    a 2D grid (matrix), unlike every other endpoint so far which
#    returns a flat list or a single object. roads[i] paired with
#    time_buckets[j] corresponds to values[i][j].
# ---------------------------------------------------------
@app.get("/api/v1/analytics/heatmap")
def get_analytics_heatmap(range_: str = Query("day", alias="range")):
    """
    Builds a road x time-bucket congestion grid.
        range=day  -> 24 time buckets (hours 0-23)
        range=week -> 7 time buckets (weekdays 0=Sunday..6=Saturday)

    NOTE: the parameter is internally named range_ (not range) because
    "range" is a Python built-in function — shadowing it would break
    any use of range() inside this function. The alias="range" keeps
    the URL query parameter itself as ?range=... per the SRS contract,
    while avoiding the shadowing bug internally. (Caught this during
    review, before it ever reached testing.)

    IMPORTANT: not every (road, bucket) combination necessarily has
    data — a road might have zero readings at some particular hour if
    data collection started partway through a day, for example. Rather
    than silently producing a ragged/incomplete grid (which would break
    frontend rendering expecting a full rectangle), missing cells are
    explicitly filled with 0 so the grid is always a complete matrix.
    """
    range_ = range_.lower().strip()
    if range_ not in ("day", "week"):
        raise HTTPException(status_code=400, detail="range must be 'day' or 'week'")

    # Day 5 optimization: this is the most expensive Analytics query —
    # it groups the ENTIRE traffic_readings table by road and time
    # bucket simultaneously. Since it aggregates over the whole
    # historical dataset (which doesn't change second-to-second the
    # way live data does), a short Redis cache means a dashboard
    # repeatedly requesting the heatmap doesn't re-run this expensive
    # aggregation on every single page load.
    cache_key = f"analytics:heatmap:{range_}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT road_id, road_name FROM roads ORDER BY road_id;")
            roads = cur.fetchall()
            if not roads:
                raise HTTPException(status_code=404, detail="No roads found")

            bucket_column = "EXTRACT(HOUR FROM recorded_at)::int" if range_ == "day" \
                else "EXTRACT(DOW FROM recorded_at)::int"
            time_buckets = list(range(24)) if range_ == "day" else list(range(7))

            cur.execute(
                f"""
                SELECT road_id, {bucket_column} AS bucket, ROUND(AVG(density), 2) AS avg_density
                FROM traffic_readings
                GROUP BY road_id, bucket
                ORDER BY road_id, bucket;
                """
            )
            raw_results = cur.fetchall()

        # Day 6: grid-building logic moved to analytics_helpers.py so it
        # can be unit tested independently of a live database connection.
        values = build_heatmap_grid(roads, time_buckets, raw_results)

        result = {
            "roads": [r["road_name"] for r in roads],
            "time_buckets": time_buckets,
            "values": values,
        }
        # Cache for 60 seconds — long enough to absorb repeated
        # dashboard loads, short enough that new historical data
        # (e.g. from a fresh generate_historical_data.py run) shows
        # up reasonably promptly.
        cache_set(cache_key, result, ttl=60)
        return result
    finally:
        conn.close()


# ---------------------------------------------------------
# NEW (Milestone 3, Day 5): GET /api/v1/analytics/reports
#    -> downloadable CSV historical report
#    Consumed by: Intern 4's report-download button
#
#    Design note: reuses the same time-range query pattern as
#    /traffic/history (M2, Day 3), across ALL roads instead of one,
#    formatted as an actual downloadable CSV file instead of JSON.
# ---------------------------------------------------------
@app.get("/api/v1/analytics/reports")
def get_analytics_report(range_: str = Query("week", alias="range"), format: str = "csv", max_rows: int = 20000):
    """
    Generates a downloadable historical report covering:
        range=day  -> last 24 hours, all roads
        range=week -> last 7 days, all roads

    Only format=csv is supported for now (per the SRS's free-tooling
    list: Python's built-in csv module). Any other format is rejected
    with a clear error rather than silently ignored.

    DEFECT FIX (Day 6): this endpoint was flagged on Day 5 as having
    the same unbounded-response risk that caused a real defect in
    Milestone 2 (Day 7) — no cap on rows returned. Added max_rows
    (default 20,000, same ceiling used for /traffic/history) plus an
    X-Total-Rows / X-Truncated response header pair, so a caller can
    tell if the download was capped, the same transparency principle
    applied to the earlier fix.
    """
    range_ = range_.lower().strip()
    format = format.lower().strip()

    if range_ not in ("day", "week"):
        raise HTTPException(status_code=400, detail="range must be 'day' or 'week'")
    if format != "csv":
        raise HTTPException(status_code=400, detail="Only format=csv is currently supported")

    max_rows = max(1, min(max_rows, 20000))

    days_back = 1 if range_ == "day" else 7
    start_ts = datetime.now() - timedelta(days=days_back)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get the true total first, so we know if this request was truncated
            cur.execute(
                "SELECT COUNT(*) AS total FROM traffic_readings WHERE recorded_at >= %s;",
                (start_ts,),
            )
            total_matching = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT r.road_name, tr.road_id, tr.vehicle_count, tr.density,
                       tr.congestion_level, tr.recorded_at
                FROM traffic_readings tr
                JOIN roads r ON r.road_id = tr.road_id
                WHERE tr.recorded_at >= %s
                ORDER BY tr.road_id, tr.recorded_at ASC
                LIMIT %s;
                """,
                (start_ts, max_rows),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No data found for the requested range")

    # Build the CSV in memory rather than writing a temp file — the
    # response is streamed straight back, nothing touches disk.
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)

    filename = f"traffic_report_{range_}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Total-Rows": str(total_matching),
            "X-Returned-Rows": str(len(rows)),
            "X-Truncated": str(total_matching > len(rows)).lower(),
        },
    )


# ---------------------------------------------------------
# NEW (Milestone 2, Day 4): GET /api/v1/traffic/road-condition/{road_id}
#    -> { road_id, status, notes, updated_at }
#    Consumed by: Intern 1's /route/conditions endpoint
# ---------------------------------------------------------
@app.get("/api/v1/traffic/road-condition/{road_id}")
def get_road_condition(road_id: int):
    """
    Returns the CURRENT (most recent) condition for a road — CLEAR,
    CONSTRUCTION, HAZARD, or CLOSED — plus a human-readable note.

    road_conditions keeps a full history (every insert is a new row,
    not an update), so "current" simply means the most recent row for
    that road_id, ordered by updated_at.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT 1 FROM roads WHERE road_id = %s;", (road_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail=f"road_id {road_id} not found")

            cur.execute(
                """
                SELECT road_id, status, notes, updated_at
                FROM road_conditions
                WHERE road_id = %s
                ORDER BY updated_at DESC
                LIMIT 1;
                """,
                (road_id,),
            )
            condition = cur.fetchone()

        if not condition:
            # Shouldn't normally happen since Day 1 seeded every road,
            # but handle it explicitly rather than crashing.
            return {"road_id": road_id, "status": "UNKNOWN", "notes": "No condition data recorded yet", "updated_at": None}

        return condition
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
