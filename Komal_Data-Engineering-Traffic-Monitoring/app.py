from fastapi import FastAPI, HTTPException
from congestion_tracker import track_congestion
from cache import set_cache, get_cache
import csv
import os

app = FastAPI(
    title="TrafficVisionAI Traffic Monitoring API",
    description="API for traffic monitoring and congestion data",
    version="1.0.0"
)

CSV_FILE = "processed_traffic.csv"


def load_data():
    """Load processed traffic data from CSV."""

    if not os.path.exists(CSV_FILE):
        raise HTTPException(
            status_code=404,
            detail="processed_traffic.csv not found"
        )

    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        data = list(reader)

    return data


@app.get("/")
def home():
    return {
        "message": "TrafficVisionAI API is running",
        "status": "success"
    }


@app.get("/traffic/live")
def get_live_traffic():
    """Return live traffic data using Redis cache."""

    # Check Redis cache first
    cached_data = get_cache("traffic_live")

    if cached_data:
        return {
            "source": "redis_cache",
            "total_records": len(cached_data),
            "traffic": cached_data
        }

    # If cache is empty, load data from CSV
    data = load_data()

    # Store data in Redis for 60 seconds
    set_cache("traffic_live", data, expiry=60)

    return {
        "source": "csv",
        "total_records": len(data),
        "traffic": data
    }


@app.get("/road/{road_id}")
def get_road_traffic(road_id: str):
    """Return traffic data for a specific road."""

    data = load_data()

    road_data = [
        row for row in data
        if row["road_id"].upper() == road_id.upper()
    ]

    if not road_data:
        raise HTTPException(
            status_code=404,
            detail=f"No traffic data found for {road_id}"
        )

    return {
        "road_id": road_id.upper(),
        "total_records": len(road_data),
        "traffic": road_data
    }


@app.get("/density")
def get_density():
    """Return traffic density and congestion information."""

    data = load_data()

    result = []

    for row in data:
        result.append({
            "road_id": row["road_id"],
            "sensor_id": row["sensor_id"],
            "density": float(row["density"]),
            "congestion": row["congestion"]
        })


    return {
        "total_records": len(result),
        "data": result
    }
@app.get("/congestion/history")
def get_congestion_history():

    history = track_congestion()

    return {
        "status": "success",
        "roads": history
    }