import json

import psycopg
import redis
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse


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
# PostgreSQL CONFIGURATION
# =========================================

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "A"
}


# =========================================
# REDIS CONFIGURATION
# =========================================

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True
)


# =========================================
# DATABASE CONNECTION
# =========================================

def get_connection():
    return psycopg.connect(**DB_CONFIG)


# =========================================
# ROOT API
# =========================================

@app.get("/")
def root():
    return {
        "message": "Traffic Monitoring Service is running"
    }


# =========================================
# LIVE TRAFFIC API
# Redis cached for 5 seconds
# =========================================

@app.get(
    "/traffic/live",
    summary="Get Live Traffic",
    description="Returns the latest live traffic readings."
)
def get_live_traffic():

    # -------------------------------------
    # 1. Check Redis cache first
    # -------------------------------------

    cached_data = redis_client.get("traffic:live")

    if cached_data:
        print("Live traffic data served from Redis cache")
        return json.loads(cached_data)

    # -------------------------------------
    # 2. If cache is empty, query PostgreSQL
    # -------------------------------------

    conn = get_connection()

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

    conn.close()

    # -------------------------------------
    # 3. Convert database rows to JSON
    # -------------------------------------

    result = [
        {
            "reading_id": row[0],
            "sensor_id": row[1],
            "road_id": row[2],
            "timestamp": row[3].isoformat(),
            "vehicle_count": row[4],
            "density": float(row[5]) if row[5] is not None else None,
            "congestion_level": row[6]
        }
        for row in rows
    ]

    # -------------------------------------
    # 4. Store result in Redis for 5 seconds
    # -------------------------------------

    redis_client.setex(
        "traffic:live",
        5,
        json.dumps(result)
    )

    print("Live traffic data loaded from PostgreSQL and cached in Redis")

    return result


# =========================================
# ROAD-SPECIFIC TRAFFIC API
# =========================================

@app.get(
    "/traffic/road/{road_id}",
    summary="Get Road Traffic",
    description="Returns traffic readings for a specific road."
)
def get_road_traffic(road_id: int):

    conn = get_connection()

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

    conn.close()

    return [
        {
            "reading_id": row[0],
            "sensor_id": row[1],
            "road_id": row[2],
            "timestamp": row[3].isoformat(),
            "vehicle_count": row[4],
            "density": float(row[5]) if row[5] is not None else None,
            "congestion_level": row[6]
        }
        for row in rows
    ]


# =========================================
# TRAFFIC DENSITY / SUMMARY API
# =========================================

@app.get(
    "/traffic/density",
    summary="Get Traffic Density",
    description="Returns traffic density and congestion information."
)
def get_traffic_density():

    conn = get_connection()

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

    conn.close()

    return [
        {
            "road_id": row[0],
            "sensor_id": row[1],
            "timestamp": row[2].isoformat(),
            "vehicle_count": row[3],
            "density": float(row[4]) if row[4] is not None else None,
            "congestion_level": row[5]
        }
        for row in rows
    ]


# =========================================
# CONGESTION HISTORY API
# =========================================

@app.get(
    "/traffic/history/{road_id}",
    summary="Get Congestion History",
    description="Returns historical traffic and congestion data for a road."
)
def get_congestion_history(road_id: int):

    conn = get_connection()

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

    conn.close()

    return [
        {
            "reading_id": row[0],
            "road_id": row[1],
            "sensor_id": row[2],
            "timestamp": row[3].isoformat(),
            "vehicle_count": row[4],
            "density": float(row[5]) if row[5] is not None else None,
            "congestion_level": row[6]
        }
        for row in rows
    ]


# =========================================
# ROAD CONDITIONS API
# =========================================

@app.get(
    "/traffic/conditions/{road_id}",
    summary="Get Road Conditions",
    description="Returns road condition information such as construction, closure, or open status."
)
def get_road_conditions(road_id: int):

    conn = get_connection()

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

    conn.close()

    return [
        {
            "condition_id": row[0],
            "road_id": row[1],
            "condition_status": row[2],
            "description": row[3],
            "start_time": row[4].isoformat() if row[4] else None,
            "end_time": row[5].isoformat() if row[5] else None,
            "created_at": row[6].isoformat() if row[6] else None
        }
        for row in rows
    ]


# =========================================
# MILESTONE 3: ALERTS API (Intern 1)
# =========================================

@app.get(
    "/alerts/my",
    summary="Get Active User Alerts",
    description="Returns active and priority traffic alerts."
)
def get_user_alerts():
    return [
        {
            "id": "ALT-101",
            "road_id": "R003",
            "road_name": "Station Road",
            "severity": "critical",
            "title": "Severe Congestion & Queue Spillback",
            "message": "Density sustained above 82% for over 15 minutes. Heavy bottleneck approaching rail terminal junction.",
            "timestamp": "2026-09-22T17:30:00Z",
            "status": "active",
            "action_recommended": "Deploy traffic dispatch officer & lengthen Northbound green signal by 25s"
        },
        {
            "id": "ALT-102",
            "road_id": "R001",
            "road_name": "MG Road",
            "severity": "warning",
            "title": "Rush Hour Volume Surge",
            "message": "Vehicle volume up 28% in past 10 minutes. Density entering high threshold (78%).",
            "timestamp": "2026-09-22T17:20:00Z",
            "status": "acknowledged",
            "action_recommended": "Broadcast variable message signage (VMS) advisory to divert toward Ring Road"
        },
        {
            "id": "ALT-103",
            "road_id": "R004",
            "road_name": "Airport Road",
            "severity": "advisory",
            "title": "Optimal Flow Corridor Identified",
            "message": "Airport arterial corridor maintaining 62 km/h free flow velocity. Recommended bypass route.",
            "timestamp": "2026-09-22T17:05:00Z",
            "status": "resolved",
            "action_recommended": "Promote route on commuter display network"
        }
    ]


@app.post(
    "/alerts/{alert_id}/read",
    summary="Mark Alert as Read / Acknowledged"
)
def mark_alert_read(alert_id: str):
    return {
        "success": True,
        "alert_id": alert_id,
        "status": "acknowledged"
    }


# =========================================
# MILESTONE 3: ANALYTICS API (Intern 2)
# =========================================

@app.get(
    "/analytics/trends",
    summary="Get Traffic Trends Time Series",
    description="Returns historical density and flow speed time series."
)
def get_analytics_trends(timeframe: str = "24h", corridor_id: str = None):
    points = []
    for h in range(24):
        is_peak = (h in [8, 9, 10, 17, 18, 19, 20])
        base_density = 80.0 if is_peak else 42.0
        points.append({
            "timestamp": f"2026-09-22T{h:02d}:00:00Z",
            "label": f"{h:02d}:00",
            "network_avg_density": base_density,
            "network_avg_speed": max(14.0, 70.0 - base_density * 0.6),
            "corridor_densities": {
                "R001": min(95.0, base_density * 1.05),
                "R002": base_density * 0.9,
                "R003": min(98.0, base_density * 1.15),
                "R004": base_density * 0.65,
                "R005": base_density * 0.8
            }
        })

    return {
        "timeframe": timeframe,
        "summary": {
            "avgDensity": 52.4,
            "avgSpeed": 38.6,
            "peakDensity": 88.0,
            "peakHour": "18:00",
            "totalVolume": 42850
        },
        "points": points
    }


@app.get(
    "/analytics/heatmap",
    summary="Get 7x24 Diurnal Congestion Heatmap Matrix"
)
def get_analytics_heatmap(corridor_id: str = None):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cells = []
    for day_idx, day_name in enumerate(days):
        is_weekend = day_idx >= 5
        for hour in range(24):
            if not is_weekend:
                base = 85.0 if hour in [8, 9, 17, 18] else 45.0 if hour in [11, 12, 13, 14, 15] else 18.0
            else:
                base = 55.0 if hour in [12, 13, 14, 15, 16, 17, 18, 19] else 20.0

            density = min(98.0, max(5.0, base))
            speed = max(12.0, 72.0 - density * 0.62)
            cells.append({
                "day_index": day_idx,
                "day_name": day_name,
                "hour": hour,
                "density": density,
                "speed": speed,
                "congestion_level": "High" if density > 65 else "Medium" if density >= 35 else "Low",
                "incident_risk": "critical" if density > 78 else "medium" if density >= 52 else "low",
                "volume_count": int(density * 2.8)
            })
    return cells


# =========================================
# MILESTONE 3: AI RECOMMENDATIONS API (Intern 3)
# =========================================

@app.get(
    "/ai/recommendations",
    summary="Get AI Decision Recommendations"
)
def get_ai_recommendations():
    return [
        {
            "id": "REC-101",
            "title": "Station Road Ingress Green Phase Extension",
            "category": "signal_retiming",
            "priority": "critical",
            "target_corridor_id": "R003",
            "target_corridor_name": "Station Road",
            "target_junction": "Terminal North Ingress (J-104)",
            "description": "Station Road density reached 82.1% with vehicle queue growing by 18 vehicles/min. Current 45s green phase causes severe spillback onto feeder arterials.",
            "action_plan": "Extend northbound cycle from 45s to 70s (+25s green) for 30 minutes, dynamically reducing cross-street phase.",
            "impact_delay_reduction_pct": 34,
            "impact_speed_gain_kmh": 8.5,
            "impact_co2_offset_pct": 16.2,
            "confidence": 0.94,
            "status": "pending",
            "simulation": {
                "baseline_delay_min": 24.5,
                "optimized_delay_min": 16.2,
                "baseline_density_pct": 82.1,
                "optimized_density_pct": 58.4,
                "queue_length_meters_before": 850,
                "queue_length_meters_after": 320
            }
        },
        {
            "id": "REC-102",
            "title": "Dynamic Bypass Detour: MG Road to Outer Ring Road",
            "category": "detour_routing",
            "priority": "high",
            "target_corridor_id": "R001",
            "target_corridor_name": "MG Road",
            "target_junction": "Victoria Flyover Divergence (J-082)",
            "description": "MG Road operating at 78.4% capacity. Diverting 20% of commercial traffic toward Outer Ring elevated bypass prevents gridlock crest.",
            "action_plan": "Update Variable Message Signs (VMS #4, #7) with advisory: 'MG Road Heavy Congestion (+18m delay) - Divert via Ring Road'.",
            "impact_delay_reduction_pct": 22,
            "impact_speed_gain_kmh": 6.2,
            "impact_co2_offset_pct": 11.5,
            "confidence": 0.89,
            "status": "pending",
            "simulation": {
                "baseline_delay_min": 19.8,
                "optimized_delay_min": 15.4,
                "baseline_density_pct": 78.4,
                "optimized_density_pct": 61.0,
                "queue_length_meters_before": 620,
                "queue_length_meters_after": 280
            }
        }
    ]


@app.post(
    "/ai/recommendations/{rec_id}/apply",
    summary="Apply AI Traffic Optimization"
)
def apply_ai_recommendation(rec_id: str):
    return {
        "success": True,
        "rec_id": rec_id,
        "status": "applied",
        "applied_at": "2026-09-22T17:35:00Z"
    }