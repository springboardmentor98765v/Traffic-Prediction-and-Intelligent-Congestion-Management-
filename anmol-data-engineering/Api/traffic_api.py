import json
import csv
import io

import psycopg
import redis

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, StreamingResponse

# =========================================
# FASTAPI CONFIGURATION
# =========================================

app = FastAPI(
    title="TrafficVision AI - Traffic Monitoring API",
    description="Real-time traffic monitoring, density analysis and congestion history.",
    version="2.0.0",
    docs_url=None
)


# =========================================
# CUSTOM SWAGGER UI
# =========================================

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():

    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="TrafficVision AI - API Documentation"
    )

    html = response.body.decode("utf-8")

    custom_css = """
    <style>

        /* =====================================
        MAIN BACKGROUND
        ===================================== */

        body {
            background: linear-gradient(
                135deg,
                #020617 0%,
                #0f172a 50%,
                #172554 100%
            ) !important;
            margin: 0;
        }


        /* =====================================
        SWAGGER CONTAINER
        ===================================== */

        .swagger-ui {
            background: transparent !important;
        }


        /* =====================================
        TOP BAR
        ===================================== */

        .swagger-ui .topbar {
            background: #020617 !important;
            border-bottom: 1px solid #1e293b;
        }

        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }


        /* =====================================
        TITLE
        ===================================== */

        .swagger-ui .info .title {
            color: #f8fafc !important;
        }

        .swagger-ui .info p,
        .swagger-ui .info li {
            color: #cbd5e1 !important;
        }


        /* =====================================
        API GROUP TITLE
        ===================================== */

        .swagger-ui .opblock-tag {
            color: #f8fafc !important;
            border-bottom: 1px solid #334155 !important;
        }


        /* =====================================
        API ENDPOINT BOXES
        ===================================== */

        .swagger-ui .opblock {
            background: rgba(15, 23, 42, 0.85) !important;
            border-radius: 10px !important;
            border: 1px solid #334155 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
        }


        /* =====================================
        ENDPOINT TEXT
        ===================================== */

        .swagger-ui .opblock .opblock-summary-path,
        .swagger-ui .opblock .opblock-summary-description {
            color: #e2e8f0 !important;
        }


        /* =====================================
        DESCRIPTION
        ===================================== */

        .swagger-ui .renderedMarkdown p {
            color: #cbd5e1 !important;
        }


        /* =====================================
        SCHEMAS
        ===================================== */

        .swagger-ui section.models {
            background: rgba(15, 23, 42, 0.85) !important;
            border: 1px solid #334155 !important;
            border-radius: 10px;
        }

        .swagger-ui section.models h4 {
            color: #f8fafc !important;
        }

        .swagger-ui .model-title {
            color: #e2e8f0 !important;
        }


        /* =====================================
        RESPONSE / PARAMETERS TEXT
        ===================================== */

        .swagger-ui table thead tr th,
        .swagger-ui table thead tr td {
            color: #e2e8f0 !important;
        }

        .swagger-ui .parameter__name,
        .swagger-ui .parameter__type {
            color: #cbd5e1 !important;
        }


        /* =====================================
        INPUT BOXES
        ===================================== */

        .swagger-ui input,
        .swagger-ui textarea,
        .swagger-ui select {
            background: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #475569 !important;
        }


        /* =====================================
        BUTTONS
        ===================================== */

        .swagger-ui .btn {
            border-radius: 6px;
        }

        .swagger-ui .btn.execute {
            background: #16a34a !important;
            border-color: #16a34a !important;
            color: white !important;
        }


        /* =====================================
        RESPONSE BOX
        ===================================== */

        .swagger-ui .responses-inner {
            background: rgba(2, 6, 23, 0.6);
        }


        /* =====================================
        FOOTER SPACE
        ===================================== */

        .swagger-ui .information-container {
            padding-top: 25px;
        }

    </style>
    """

    html = html.replace("</head>", custom_css + "</head>")

    return HTMLResponse(content=html)



# =========================================
# CONFIGURATION
# =========================================

import os

from fastapi import HTTPException


# PostgreSQL configuration
# Environment variables are preferred. The defaults keep the existing
# local-development setup working.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "A"),
}


# Redis configuration
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)


# =========================================
# DATABASE HELPERS
# =========================================

def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg.connect(**DB_CONFIG)


def row_to_traffic_dict(row):
    """Convert a standard traffic query row into JSON-safe data."""
    return {
        "reading_id": row[0],
        "sensor_id": row[1],
        "road_id": row[2],
        "timestamp": row[3].isoformat() if row[3] else None,
        "vehicle_count": row[4],
        "density": float(row[5]) if row[5] is not None else None,
        "congestion_level": row[6],
    }


def validate_bucket(value: str) -> str:
    if value not in {"hour", "day"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid bucket. Use 'hour' or 'day'.",
        )
    return value


# =========================================
# ROOT API
# =========================================

@app.get(
    "/",
    summary="Health Check",
    description="Checks whether the TrafficVision AI API is running.",
)
def root():
    return {
        "message": "Traffic Monitoring Service is running",
        "status": "ok",
    }


# =========================================
# LIVE TRAFFIC API
# Redis cached for 5 seconds
# =========================================

@app.get(
    "/traffic/live",
    summary="Get Live Traffic",
    description="Returns the latest live traffic readings.",
)
def get_live_traffic():
    cache_key = "traffic:live"

    # Redis is a cache, so a Redis failure must not make the API unavailable.
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("Live traffic data served from Redis cache")
            return json.loads(cached_data)
    except (redis.RedisError, json.JSONDecodeError) as exc:
        print(f"Redis cache read skipped: {exc}")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    tr.reading_id,
                    tr.sensor_id,
                    s.road_id,
                    tr.timestamp,
                    tr.vehicle_count,
                    tr.density,
                    tr.congestion_level
                FROM traffic_readings tr
                JOIN sensors s
                    ON tr.sensor_id = s.sensor_id
                ORDER BY tr.timestamp DESC
                LIMIT 50;
            """)
            rows = cur.fetchall()

        result = [row_to_traffic_dict(row) for row in rows]

    finally:
        conn.close()

    try:
        redis_client.setex(cache_key, 5, json.dumps(result))
        print("Live traffic data loaded from PostgreSQL and cached in Redis")
    except redis.RedisError as exc:
        print(f"Redis cache write skipped: {exc}")

    return result


# =========================================
# ROAD-SPECIFIC TRAFFIC API
# =========================================

@app.get(
    "/traffic/road/{road_id}",
    summary="Get Road Traffic",
    description="Returns traffic readings for a specific road.",
)
def get_road_traffic(road_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    tr.reading_id,
                    tr.sensor_id,
                    s.road_id,
                    tr.timestamp,
                    tr.vehicle_count,
                    tr.density,
                    tr.congestion_level
                FROM traffic_readings tr
                JOIN sensors s
                    ON tr.sensor_id = s.sensor_id
                WHERE s.road_id = %s
                ORDER BY tr.timestamp DESC
                LIMIT 50;
            """, (road_id,))
            rows = cur.fetchall()

        return [row_to_traffic_dict(row) for row in rows]
    finally:
        conn.close()


# =========================================
# TRAFFIC DENSITY / SUMMARY API
# =========================================

@app.get(
    "/traffic/density",
    summary="Get Traffic Density",
    description="Returns traffic density and congestion information.",
)
def get_traffic_density():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    s.road_id,
                    tr.sensor_id,
                    tr.timestamp,
                    tr.vehicle_count,
                    tr.density,
                    tr.congestion_level
                FROM traffic_readings tr
                JOIN sensors s
                    ON tr.sensor_id = s.sensor_id
                ORDER BY tr.timestamp DESC
                LIMIT 50;
            """)
            rows = cur.fetchall()

        return [
            {
                "road_id": row[0],
                "sensor_id": row[1],
                "timestamp": row[2].isoformat() if row[2] else None,
                "vehicle_count": row[3],
                "density": float(row[4]) if row[4] is not None else None,
                "congestion_level": row[5],
            }
            for row in rows
        ]
    finally:
        conn.close()


# =========================================
# CONGESTION HISTORY API
# =========================================

@app.get(
    "/traffic/history/{road_id}",
    summary="Get Congestion History",
    description="Returns historical traffic and congestion data for a road.",
)
def get_congestion_history(road_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    tr.reading_id,
                    s.road_id,
                    tr.sensor_id,
                    tr.timestamp,
                    tr.vehicle_count,
                    tr.density,
                    tr.congestion_level
                FROM traffic_readings tr
                JOIN sensors s
                    ON tr.sensor_id = s.sensor_id
                WHERE s.road_id = %s
                ORDER BY tr.timestamp ASC;
            """, (road_id,))
            rows = cur.fetchall()

        return [
            {
                "reading_id": row[0],
                "road_id": row[1],
                "sensor_id": row[2],
                "timestamp": row[3].isoformat() if row[3] else None,
                "vehicle_count": row[4],
                "density": float(row[5]) if row[5] is not None else None,
                "congestion_level": row[6],
            }
            for row in rows
        ]
    finally:
        conn.close()


# =========================================
# ROAD CONDITIONS API
# =========================================

@app.get(
    "/traffic/conditions/{road_id}",
    summary="Get Road Conditions",
    description=(
        "Returns road condition information such as construction, "
        "closure, or open status."
    ),
)
def get_road_conditions(road_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    condition_id,
                    road_id,
                    condition_status,
                    description,
                    start_time,
                    end_time,
                    created_at
                FROM road_conditions
                WHERE road_id = %s
                ORDER BY start_time DESC;
            """, (road_id,))
            rows = cur.fetchall()

        return [
            {
                "condition_id": row[0],
                "road_id": row[1],
                "condition_status": row[2],
                "description": row[3],
                "start_time": row[4].isoformat() if row[4] else None,
                "end_time": row[5].isoformat() if row[5] else None,
                "created_at": row[6].isoformat() if row[6] else None,
            }
            for row in rows
        ]
    finally:
        conn.close()


# =========================================
# ANALYTICS HELPERS
# =========================================

# Milestone 3 SRS contract:
#   trends  -> range=day|week
#   heatmap -> range=day|week|month (default week)
#   reports -> range + format=csv
#
# The service keeps the existing internal /analytics/* paths. If the
# API Gateway exposes them under /api/v1, the gateway should continue
# to add/remove that prefix rather than changing the internal service.

ANALYTICS_DEFAULT_RANGE = "week"
REPORT_PREVIEW_PAGE_SIZE = 25
REPORT_MAX_PAGE_SIZE = 100
CSV_FETCH_SIZE = 1000


def validate_analytics_range(value: str, allowed=None) -> str:
    """Validate a time range before it reaches SQL construction."""
    if allowed is None:
        allowed = {"day", "week", "month"}

    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid range. Use one of: {allowed_text}.",
        )

    return value


def analytics_range_filter(range_value: str) -> str:
    """Return a fixed SQL fragment for a validated analytics range.

    Do not use INTERVAL %s here. PostgreSQL does not accept a bind
    parameter directly after INTERVAL. Fixed, validated SQL fragments
    avoid the syntax error that caused the earlier /analytics/reports
    500 response.
    """
    filters = {
        "day": "AND tr.timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 day'",
        "week": "AND tr.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'",
        "month": "AND tr.timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'",
    }
    return filters[range_value]


def congestion_score_sql(column: str = "tr.congestion_level") -> str:
    """Map LOW/MEDIUM/HIGH/SEVERE to a numeric 1-4 congestion score."""
    return f"""
        CASE {column}
            WHEN 'LOW' THEN 1.0
            WHEN 'MEDIUM' THEN 2.0
            WHEN 'HIGH' THEN 3.0
            WHEN 'SEVERE' THEN 4.0
            ELSE NULL
        END
    """


def row_to_report_dict(row):
    """Convert a report row to JSON-safe data."""
    return {
        "reading_id": row[0],
        "sensor_id": row[1],
        "road_id": row[2],
        "timestamp": row[3].isoformat() if row[3] else None,
        "vehicle_count": row[4],
        "density": float(row[5]) if row[5] is not None else None,
        "congestion_level": row[6],
    }


# =========================================
# ANALYTICS - TREND ANALYSIS API
# =========================================

@app.get(
    "/analytics/trends",
    summary="Get Traffic Trends",
    description=(
        "Returns daily/weekly traffic congestion patterns per road. "
        "The SRS contract uses range=day or range=week. "
        "Day returns hourly points; week returns daily points."
    ),
)
def get_traffic_trends(
    road_id: int | None = None,
    range: str = "week",
):
    range = validate_analytics_range(range, {"day", "week"})

    # For a one-day view, hourly points make the dashboard useful.
    # For a one-week view, daily points keep the response compact.
    bucket = "hour" if range == "day" else "day"
    time_expression = f"DATE_TRUNC('{bucket}', tr.timestamp)"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = f"""
                SELECT
                    {time_expression} AS period,
                    s.road_id,
                    ROUND(AVG({congestion_score_sql()}), 2) AS avg_congestion
                FROM traffic_readings tr
                JOIN sensors s
                    ON tr.sensor_id = s.sensor_id
                WHERE 1 = 1
                    {analytics_range_filter(range)}
            """
            params = []

            if road_id is not None:
                query += " AND s.road_id = %s"
                params.append(road_id)

            query += f"""
                GROUP BY {time_expression}, s.road_id
                ORDER BY period ASC, s.road_id ASC;
            """

            cur.execute(query, params)
            rows = cur.fetchall()

        points = [
            {
                "period": row[0].isoformat() if row[0] else None,
                "road_id": row[1],
                "avg_congestion": float(row[2]) if row[2] is not None else None,
            }
            for row in rows
        ]

        return {
            "road_id": road_id,
            "range": range,
            "points": points,
        }
    finally:
        conn.close()


# =========================================
# ANALYTICS - HEATMAP API
# =========================================

@app.get(
    "/analytics/heatmap",
    summary="Get Traffic Heatmap",
    description=(
        "Returns congestion heatmap grid data across roads and time buckets. "
        "Values are congestion scores: LOW=1, MEDIUM=2, HIGH=3, SEVERE=4."
    ),
)
def get_traffic_heatmap(
    range: str = "week",
    road_id: int | None = None,
    bucket: str = "hour",
):
    range = validate_analytics_range(range, {"day", "week", "month"})
    bucket = validate_bucket(bucket)

    time_expression = (
        "DATE_TRUNC('hour', tr.timestamp)"
        if bucket == "hour"
        else "DATE_TRUNC('day', tr.timestamp)"
    )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = f"""
                SELECT
                    s.road_id,
                    {time_expression} AS time_bucket,
                    ROUND(AVG({congestion_score_sql()}), 2) AS congestion_score
                FROM traffic_readings tr
                JOIN sensors s
                    ON tr.sensor_id = s.sensor_id
                WHERE 1 = 1
                    {analytics_range_filter(range)}
            """
            params = []

            if road_id is not None:
                query += " AND s.road_id = %s"
                params.append(road_id)

            query += f"""
                GROUP BY s.road_id, {time_expression}
                ORDER BY s.road_id ASC, time_bucket ASC;
            """

            cur.execute(query, params)
            rows = cur.fetchall()

        # Build the exact grid shape expected by the Milestone 3 SRS:
        # roads[] x time_buckets[] -> values[][].
        roads = sorted({row[0] for row in rows})
        time_buckets = sorted(
            {
                row[1].isoformat()
                for row in rows
                if row[1] is not None
            }
        )

        lookup = {
            (row[0], row[1].isoformat() if row[1] else None): (
                float(row[2]) if row[2] is not None else 0.0
            )
            for row in rows
        }

        values = [
            [lookup.get((road, time_bucket), 0.0) for time_bucket in time_buckets]
            for road in roads
        ]

        return {
            "range": range,
            "bucket": bucket,
            "road_id": road_id,
            "roads": roads,
            "time_buckets": time_buckets,
            "values": values,
        }
    finally:
        conn.close()


# =========================================
# ANALYTICS - HISTORICAL REPORT API
# =========================================


def report_base_query(range_value: str, road_id: int | None = None):
    """Return the common FROM/WHERE part and its parameters."""
    query = """
        FROM traffic_readings tr
        JOIN sensors s
            ON tr.sensor_id = s.sensor_id
        WHERE 1 = 1
    """
    params = []

    if range_value != "all":
        query += f"\n            {analytics_range_filter(range_value)}\n"

    if road_id is not None:
        query += " AND s.road_id = %s\n"
        params.append(road_id)

    return query, params


def traffic_csv_stream(range_value: str, road_id: int | None):
    """Stream CSV rows without loading the complete report into memory."""
    conn = get_connection()

    try:
        base_query, params = report_base_query(range_value, road_id)

        query = """
            SELECT
                tr.reading_id,
                tr.sensor_id,
                s.road_id,
                tr.timestamp,
                tr.vehicle_count,
                tr.density,
                tr.congestion_level
        """ + base_query + """
            ORDER BY tr.timestamp ASC, s.road_id ASC, tr.sensor_id ASC;
        """

        # A server-side cursor prevents a large historical report from being
        # fully loaded into RAM before StreamingResponse starts sending data.
        with conn.cursor(name="traffic_report_export") as cur:
            cur.execute(query, params)

            header = io.StringIO(newline="")
            writer = csv.writer(header)
            writer.writerow([
                "reading_id",
                "sensor_id",
                "road_id",
                "timestamp",
                "vehicle_count",
                "density",
                "congestion_level",
            ])
            yield header.getvalue()

            while True:
                rows = cur.fetchmany(CSV_FETCH_SIZE)
                if not rows:
                    break

                chunk = io.StringIO(newline="")
                writer = csv.writer(chunk)

                for row in rows:
                    writer.writerow([
                        row[0],
                        row[1],
                        row[2],
                        row[3].isoformat() if row[3] else None,
                        row[4],
                        float(row[5]) if row[5] is not None else None,
                        row[6],
                    ])

                yield chunk.getvalue()
    finally:
        conn.close()


@app.get(
    "/analytics/reports",
    summary="Generate Historical Traffic Report",
    description=(
        "Generates a downloadable historical traffic CSV report. "
        "JSON is available as a small paginated preview for Swagger so the "
        "documentation page never has to render thousands of records."
    ),
)
def get_traffic_report(
    road_id: int | None = None,
    range: str = "week",
    format: str = "json",
    page: int = 1,
    page_size: int = REPORT_PREVIEW_PAGE_SIZE,
):
    # 'all' is intentionally supported only for the downloadable report.
    # Swagger's default remains week + JSON so the demo is fast and readable.
    range = validate_analytics_range(range, {"day", "week", "month", "all"})

    if format not in {"json", "csv"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Use 'json' or 'csv'.",
        )

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="page must be greater than or equal to 1.",
        )

    if page_size < 1 or page_size > REPORT_MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"page_size must be between 1 and {REPORT_MAX_PAGE_SIZE}.",
        )

    # -------------------------------------------------
    # CSV: actual downloadable historical report.
    # It is streamed and therefore does not freeze Swagger
    # or the API process while building a large in-memory string.
    # -------------------------------------------------
    if format == "csv":
        filename = "traffic_historical_report.csv"
        if road_id is not None:
            filename = f"traffic_report_road_{road_id}.csv"

        return StreamingResponse(
            traffic_csv_stream(range, road_id),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    # -------------------------------------------------
    # JSON: intentionally a small preview only.
    # Fetch one extra row so we can report has_more without
    # running a potentially expensive COUNT(*) over all history.
    # -------------------------------------------------
    offset = (page - 1) * page_size
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            base_query, params = report_base_query(range, road_id)

            query = """
                SELECT
                    tr.reading_id,
                    tr.sensor_id,
                    s.road_id,
                    tr.timestamp,
                    tr.vehicle_count,
                    tr.density,
                    tr.congestion_level
            """ + base_query + """
                ORDER BY tr.timestamp ASC, s.road_id ASC, tr.sensor_id ASC
                LIMIT %s OFFSET %s;
            """

            cur.execute(query, params + [page_size + 1, offset])
            rows = cur.fetchall()

        has_more = len(rows) > page_size
        rows = rows[:page_size]
        data = [row_to_report_dict(row) for row in rows]

        return {
            "report_type": "historical_traffic",
            "range": range,
            "road_id": road_id,
            "format": "json_preview",
            "page": page,
            "page_size": page_size,
            "returned_records": len(data),
            "has_more": has_more,
            "data": data,
        }
    finally:
        conn.close()
