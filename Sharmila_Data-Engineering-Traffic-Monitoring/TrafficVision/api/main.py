
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import psycopg2
import redis
import json
import pandas as pd
from io import StringIO

from analytics.trend_analysis import (
    load_data as load_trend_data,
    generate_daily_trends,
    generate_weekly_trends,
    create_daily_output,
    create_weekly_output,
)

from analytics.heatmap_analysis import (
    load_data as load_heatmap_data,
    generate_heatmap,
    create_heatmap_output,
)

app = FastAPI(title="TrafficVision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "traffic_history_clean.csv"
CONGESTION_THRESHOLD = 0.70


def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="trafficvision",
        user="postgres",
        password="password",
    )


r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


@app.get("/")
def home():
    return {"message": "TrafficVision API is running"}


@app.get("/traffic/live")
def live_traffic():
    cached_data = r.get("traffic:live")

    if cached_data:
        return json.loads(cached_data)

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                road_id,
                recorded_at AS timestamp,
                vehicle_count,
                density,
                congestion_level
            FROM traffic_records
            WHERE road_id <> 4
            ORDER BY recorded_at DESC
            LIMIT 10
        """)

        rows = cur.fetchall()

        result = [
            {
                "road_id": row[0],
                "timestamp": row[1],
                "vehicle_count": row[2],
                "density": float(row[3]),
                "congestion_level": row[4],
            }
            for row in rows
        ]

        r.set(
            "traffic:live",
            json.dumps(result, default=str),
            ex=30,
        )

        return result
    finally:
        cur.close()
        conn.close()


@app.get("/traffic/road/{road_id}")
def traffic_by_road(road_id: int):
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available")
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                road_id,
                recorded_at AS timestamp,
                vehicle_count,
                density,
                congestion_level
            FROM traffic_records
            WHERE road_id = %s AND road_id <> 4
            ORDER BY recorded_at DESC
            LIMIT 20
        """, (road_id,))

        rows = cur.fetchall()

        return [
            {
                "road_id": row[0],
                "timestamp": row[1],
                "vehicle_count": row[2],
                "density": float(row[3]),
                "congestion_level": row[4],
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()



@app.get("/traffic/density")
def traffic_density():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT road_id, recorded_at, density, congestion_level
            FROM traffic_records
            WHERE road_id <> 4
            ORDER BY recorded_at DESC
            LIMIT 20
        """)
        rows = cur.fetchall()
        return [
            {
                "road_id": row[0],
                "timestamp": row[1],
                "density": float(row[2]) if row[2] is not None else None,
                "congestion_level": row[3],
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.get("/traffic/utilization")
def traffic_utilization():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT road_id,
                   COUNT(*) AS total_records,
                   AVG(vehicle_count) AS avg_vehicle_count,
                   MAX(vehicle_count) AS max_vehicle_count,
                   AVG(density) AS avg_density
            FROM traffic_records
            WHERE road_id <> 4
            GROUP BY road_id
            ORDER BY road_id
        """)
        rows = cur.fetchall()
        return [
            {
                "road_id": row[0],
                "total_records": row[1],
                "avg_vehicle_count": float(row[2]) if row[2] is not None else None,
                "max_vehicle_count": row[3],
                "avg_density": float(row[4]) if row[4] is not None else None,
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.get("/traffic/congestion/history")
def congestion_history():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT road_id, recorded_at, congestion_level
            FROM traffic_records
            WHERE road_id <> 4
            ORDER BY recorded_at DESC
            LIMIT 100
        """)
        rows = cur.fetchall()
        return [
            {
                "road_id": row[0],
                "timestamp": row[1],
                "congestion_level": row[2],
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.get("/traffic/history")
def traffic_history(road_id: int, start: str, end: str):
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT road_id,
                   recorded_at,
                   vehicle_count,
                   density,
                   congestion_level
            FROM traffic_records
            WHERE road_id = %s
              AND road_id <> 4
              AND recorded_at >= %s
              AND recorded_at <= %s
            ORDER BY recorded_at ASC
        """, (road_id, start, end))
        rows = cur.fetchall()
        return [
            {
                "road_id": row[0],
                "timestamp": row[1],
                "vehicle_count": row[2],
                "density": float(row[3]) if row[3] is not None else None,
                "congestion_level": row[4],
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.get("/traffic/aggregate")
def traffic_aggregate(
    road_id: int,
    start: str,
    end: str,
    interval: str = "hour",
):
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available")

    if interval not in ["hour", "day"]:
        raise HTTPException(
            status_code=400,
            detail="interval must be either 'hour' or 'day'",
        )

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT road_id,
                   DATE_TRUNC(%s, recorded_at) AS period,
                   AVG(vehicle_count) AS avg_vehicle_count,
                   AVG(density) AS avg_density
            FROM traffic_records
            WHERE road_id = %s
              AND road_id <> 4
              AND recorded_at >= %s
              AND recorded_at <= %s
            GROUP BY road_id, DATE_TRUNC(%s, recorded_at)
            ORDER BY period ASC
        """, (interval, road_id, start, end, interval))
        rows = cur.fetchall()
        return [
            {
                "road_id": row[0],
                "timestamp": row[1],
                "avg_vehicle_count": float(row[2]) if row[2] is not None else None,
                "avg_density": float(row[3]) if row[3] is not None else None,
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.get("/traffic/road-condition/{road_id}")
def get_road_condition(road_id: int):
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available")
    conn = get_connection()
    cur = conn.cursor()

    try:
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

        return [
            {
                "id": row[0],
                "road_id": row[1],
                "condition_type": row[2],
                "description": row[3],
                "is_active": row[4],
                "updated_at": row[5],
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()


# ANALYTICS: TRAFFIC TRENDS

@app.get("/analytics/trends", tags=["Analytics"])
def analytics_trends(
    road_id: int = 1,
    range: str = "day",
):
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available")

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


# ANALYTICS: TRAFFIC HEATMAP

@app.get("/analytics/heatmap", tags=["Analytics"])
def analytics_heatmap():
    df = load_heatmap_data()
    matrix = generate_heatmap(df)
    return create_heatmap_output(matrix)


# ANALYTICS: CONGESTION ALERTS

@app.get("/analytics/alerts", tags=["Analytics"])
def analytics_alerts(road_id: int | None = None):
    df = pd.read_csv(DATA_FILE)
    df = df[df["road_id"] != 4]
    alerts = df[df["density"] >= CONGESTION_THRESHOLD].copy()

    if road_id is not None:
        alerts = alerts[alerts["road_id"] == road_id]

    alerts["alert_type"] = "congestion"
    alerts["message"] = alerts["road_id"].apply(
        lambda road: f"High congestion detected on Road {int(road)}"
    )

    return alerts.to_dict(orient="records")


@app.get("/analytics/alerts/summary", tags=["Analytics"])
def analytics_alert_summary():
    df = pd.read_csv(DATA_FILE)
    df = df[df["road_id"] != 4]
    alerts = df[df["density"] >= CONGESTION_THRESHOLD]

    road_counts = {
        str(int(road_id)): int(count)
        for road_id, count in alerts.groupby("road_id").size().items()
    }

    return {
        "threshold": CONGESTION_THRESHOLD,
        "total_records": len(df),
        "threshold_breaches": len(alerts),
        "road_wise_breaches": road_counts,
    }


# ANALYTICS: CSV REPORTS

@app.get("/analytics/reports", tags=["Analytics"])
def analytics_reports(
    range: str = "day",
    format: str = "csv",
):
    if range not in ["day", "week"]:
        return {"error": "range must be day or week"}

    if format != "csv":
        return {"error": "Only csv format is supported"}

    df = pd.read_csv(DATA_FILE)
    df = df[df["road_id"] != 4]
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if range == "week":
        df["week"] = (
            df["timestamp"]
            .dt.to_period("W")
            .apply(lambda period: period.start_time.date())
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
        },
    )
