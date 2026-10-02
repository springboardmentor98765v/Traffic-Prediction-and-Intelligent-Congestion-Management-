from fastapi import FastAPI
import psycopg2
import redis
import json
from analytics.trend_analysis import (
    load_data as load_trend_data,
    generate_daily_trends,
    generate_weekly_trends,
    create_daily_output,
    create_weekly_output
)

from analytics.heatmap_analysis import (
    load_data as load_heatmap_data,
    generate_heatmap,
    create_heatmap_output
)

import pandas as pd
from io import StringIO
from fastapi.responses import StreamingResponse

from analytics.trend_analysis import (
    load_data as load_trend_data,
    generate_daily_trends,
    generate_weekly_trends,
    create_daily_output,
    create_weekly_output
)

from analytics.heatmap_analysis import (
    load_data as load_heatmap_data,
    generate_heatmap,
    create_heatmap_output
)

app = FastAPI(title="TrafficVision API")

# PostgreSQL connection

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="trafficvision",
        user="postgres",
        password="sharmila0612"
    )
    
# Redis connection

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# Home

@app.get("/")
def home():
    return {
        "message": "TrafficVision API is running"
    }

# Live Traffic

@app.get("/traffic/live")
def live_traffic():

    # Check Redis cache first
    cached_data = r.get("traffic:live")

    if cached_data:
        return json.loads(cached_data)

    # If cache does not exist,
    # get data from PostgreSQL
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            road_id,
            timestamp,
            vehicle_count,
            density,
            congestion_level
        FROM traffic_data
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert database rows into JSON format
    result = [
        {
            "road_id": row[0],
            "timestamp": row[1],
            "vehicle_count": row[2],
            "density": float(row[3]),
            "congestion_level": row[4]
        }
        for row in rows
    ]

    # Store result in Redis for 30 seconds
    r.set(
        "traffic:live",
        json.dumps(result, default=str),
        ex=30
    )

    return result

#  Traffic By Road

@app.get("/traffic/road/{road_id}")
def traffic_by_road(road_id: int):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            road_id,
            timestamp,
            vehicle_count,
            density,
            congestion_level
        FROM traffic_data
        WHERE road_id = %s
        ORDER BY timestamp DESC
        LIMIT 20
    """, (road_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "road_id": row[0],
            "timestamp": row[1],
            "vehicle_count": row[2],
            "density": float(row[3]),
            "congestion_level": row[4]
        }
        for row in rows
    ]


#  Traffic Density

@app.get("/traffic/density")
def traffic_density():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            road_id,
            timestamp,
            density,
            congestion_level
        FROM traffic_data
        ORDER BY timestamp DESC
        LIMIT 20
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "road_id": row[0],
            "timestamp": row[1],
            "density": float(row[2]),
            "congestion_level": row[3]
        }
        for row in rows
    ]


#  Traffic Utilization

@app.get("/traffic/utilization")
def traffic_utilization():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            road_id,
            COUNT(*) AS total_records,
            AVG(vehicle_count) AS avg_vehicle_count,
            MAX(vehicle_count) AS max_vehicle_count,
            AVG(density) AS avg_density
        FROM traffic_data
        GROUP BY road_id
        ORDER BY road_id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "road_id": row[0],
            "total_records": row[1],
            "avg_vehicle_count": float(row[2]),
            "max_vehicle_count": row[3],
            "avg_density": float(row[4])
        }
        for row in rows
    ]


# Congestion History

@app.get("/traffic/congestion/history")
def congestion_history():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            road_id,
            timestamp,
            congestion_level
        FROM traffic_data
        ORDER BY timestamp DESC
        LIMIT 100
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "road_id": row[0],
            "timestamp": row[1],
            "congestion_level": row[2]
        }
        for row in rows
    ]
    
# Historical Traffic Data

@app.get("/traffic/history")
def traffic_history(
    road_id: int,
    start: str,
    end: str
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            road_id,
            timestamp,
            vehicle_count,
            density,
            congestion_level
        FROM traffic_history
        WHERE road_id = %s
          AND timestamp >= %s
          AND timestamp <= %s
        ORDER BY timestamp ASC
    """, (road_id, start, end))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "road_id": row[0],
            "timestamp": row[1],
            "vehicle_count": row[2],
            "density": float(row[3]),
            "congestion_level": row[4]
        }
        for row in rows
    ]
    
# Historical Traffic Aggregation

@app.get("/traffic/aggregate")
def traffic_aggregate(
    road_id: int,
    start: str,
    end: str,
    interval: str = "hour"
):

    if interval not in ["hour", "day"]:
        return {
            "error": "interval must be either 'hour' or 'day'"
        }

    conn = get_connection()
    cur = conn.cursor()

    if interval == "hour":
        group_interval = "hour"
    else:
        group_interval = "day"

    query = f"""
        SELECT
            road_id,
            DATE_TRUNC('{group_interval}', timestamp) AS period,
            AVG(vehicle_count) AS avg_vehicle_count,
            AVG(density) AS avg_density
        FROM traffic_history
        WHERE road_id = %s
          AND timestamp >= %s
          AND timestamp <= %s
        GROUP BY road_id, DATE_TRUNC('{group_interval}', timestamp)
        ORDER BY period ASC
    """

    cur.execute(query, (road_id, start, end))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "road_id": row[0],
            "timestamp": row[1],
            "avg_vehicle_count": float(row[2]),
            "avg_density": float(row[3])
        }
        for row in rows
    ]
    
# Road Conditions

@app.get("/traffic/road-condition/{road_id}")
def get_road_condition(road_id: int):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            road_id,
            condition_type,
            description,
            is_active,
            updated_at
        FROM road_conditions
        WHERE road_id = %s
        ORDER BY updated_at DESC
    """, (road_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "road_id": row[1],
            "condition_type": row[2],
            "description": row[3],
            "is_active": row[4],
            "updated_at": row[5]
        }
        for row in rows
    ]
    

# ANALYTICS - TRAFFIC TRENDS

@app.get("/analytics/trends", tags=["Analytics"])
def analytics_trends(
    road_id: int = 1,
    range: str = "day"
):
    if range not in ["day", "week"]:
        return {"error": "range must be day or week"}

    df = load_trend_data()

    if range == "day":
        trends = generate_daily_trends(df)
        return create_daily_output(trends, road_id)

    trends = generate_weekly_trends(df)
    return create_weekly_output(trends, road_id)


# ANALYTICS - TRAFFIC HEATMAP


@app.get("/analytics/heatmap", tags=["Analytics"])
def analytics_heatmap():
    df = load_heatmap_data()

    matrix = generate_heatmap(df)

    return create_heatmap_output(matrix)

# =====================================
# MILESTONE 3 - ANALYTICS APIs
# =====================================

DATA_FILE = "traffic_history_clean.csv"
CONGESTION_THRESHOLD = 0.70


# 1. Congestion Alerts

@app.get("/analytics/alerts", tags=["Analytics"])
def analytics_alerts(road_id: int = None):

    df = pd.read_csv(DATA_FILE)

    alerts = df[df["density"] >= CONGESTION_THRESHOLD].copy()

    if road_id is not None:
        alerts = alerts[alerts["road_id"] == road_id]

    alerts["alert_type"] = "congestion"
    alerts["message"] = alerts["road_id"].apply(
        lambda road: f"High congestion detected on Road {int(road)}"
    )

    return alerts.to_dict(orient="records")


# 2. Congestion Alert Summary

@app.get("/analytics/alerts/summary", tags=["Analytics"])
def analytics_alert_summary():

    df = pd.read_csv(DATA_FILE)

    alerts = df[df["density"] >= CONGESTION_THRESHOLD]

    road_counts = (
        alerts.groupby("road_id")
        .size()
        .to_dict()
    )

    return {
        "threshold": CONGESTION_THRESHOLD,
        "total_records": len(df),
        "threshold_breaches": len(alerts),
        "road_wise_breaches": road_counts
    }


# 3. Daily and Weekly Trends

@app.get("/analytics/trends", tags=["Analytics"])
def analytics_trends(road_id: int = 1, range: str = "day"):

    if range not in ["day", "week"]:
        return {"error": "range must be day or week"}

    df = load_trend_data()

    if road_id not in df["road_id"].unique():
        return {"error": "Invalid road_id"}

    if range == "day":
        trends = generate_daily_trends(df)
        return create_daily_output(trends, road_id)

    trends = generate_weekly_trends(df)
    return create_weekly_output(trends, road_id)


# 4. Traffic Heatmap

@app.get("/analytics/heatmap", tags=["Analytics"])
def analytics_heatmap():

    df = load_heatmap_data()
    matrix = generate_heatmap(df)

    return create_heatmap_output(matrix)


# 5. Historical CSV Reports

@app.get("/analytics/reports", tags=["Analytics"])
def analytics_reports(range: str = "day", format: str = "csv"):

    if range not in ["day", "week"]:
        return {"error": "range must be day or week"}

    if format != "csv":
        return {"error": "Only csv format is supported"}

    df = pd.read_csv(DATA_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if range == "week":
        df["week"] = (
            df["timestamp"]
            .dt.to_period("W")
            .apply(lambda x: x.start_time.date())
        )

    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    filename = f"historical_traffic_{range}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )