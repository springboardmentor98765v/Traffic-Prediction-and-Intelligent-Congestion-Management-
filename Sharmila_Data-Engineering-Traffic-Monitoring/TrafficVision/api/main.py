from fastapi import FastAPI
import psycopg2
import redis
import json


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