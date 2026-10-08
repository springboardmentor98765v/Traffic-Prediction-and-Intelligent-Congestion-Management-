import csv
import os
import time
from pathlib import Path
from datetime import datetime

import psycopg2

from congestion_calculator import calculate_congestion
from app.redis_cache import (
    cache_latest_reading,
    get_redis_client,
    clear_live_traffic_cache,
)

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "traffic_monitoring_synthetic_dataset_with_density.csv"
)


REQUIRED_FIELDS = {
    "road_id",
    "sensor_id",
    "timestamp",
    "vehicle_count",
    "avg_speed_kmph",
    "road_capacity",
    "traffic_density_vehicles_per_km",
    "latitude",
    "longitude",
}


INSERT_SQL = """
INSERT INTO traffic_readings (
    road_id,
    sensor_id,
    reading_timestamp,
    vehicle_count,
    avg_speed_kmph,
    road_capacity,
    traffic_density_vehicles_per_km,
    congestion_level,
    latitude,
    longitude
)
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s
)
"""


def validate_ingestion_row(row: dict) -> bool:
    """Validate one CSV traffic row before database insertion."""
    missing = REQUIRED_FIELDS - set(row.keys())
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")

    if not row["road_id"].strip():
        raise ValueError("road_id cannot be empty")
    if not row["sensor_id"].strip():
        raise ValueError("sensor_id cannot be empty")

    try:
        datetime.fromisoformat(row["timestamp"].replace(" ", "T"))
    except ValueError as exc:
        raise ValueError("Invalid timestamp") from exc

    vehicle_count = int(row["vehicle_count"])
    avg_speed = float(row["avg_speed_kmph"])
    road_capacity = int(row["road_capacity"])
    density = float(row["traffic_density_vehicles_per_km"])

    if vehicle_count < 0:
        raise ValueError("vehicle_count cannot be negative")
    if avg_speed < 0:
        raise ValueError("avg_speed_kmph cannot be negative")
    if road_capacity <= 0:
        raise ValueError("road_capacity must be greater than 0")
    if density < 0:
        raise ValueError("traffic density cannot be negative")

    float(row["latitude"])
    float(row["longitude"])

    return True


def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "traffic_monitoring"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def ingest(max_records=None):
    interval = float(os.getenv("INGEST_INTERVAL_SECONDS", "5"))
    inserted = 0

    pg = get_postgres_connection()
    rds = get_redis_client()

    try:
        with pg.cursor() as cur:
            with open(DATA_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    validate_ingestion_row(row)

                    congestion = calculate_congestion(
                        int(row["vehicle_count"]),
                        int(row["road_capacity"]),
                    )

                    values = (
                        row["road_id"],
                        row["sensor_id"],
                        row["timestamp"],
                        int(row["vehicle_count"]),
                        float(row["avg_speed_kmph"]),
                        int(row["road_capacity"]),
                        float(row["traffic_density_vehicles_per_km"]),
                        congestion,
                        float(row["latitude"]),
                        float(row["longitude"]),
                    )

                    cur.execute(INSERT_SQL, values)
                    pg.commit()

                    cache_latest_reading(
                        rds,
                        {
                            "road_id": row["road_id"],
                            "sensor_id": row["sensor_id"],
                            "timestamp": row["timestamp"],
                            "vehicle_count": int(row["vehicle_count"]),
                            "avg_speed_kmph": float(row["avg_speed_kmph"]),
                            "density_vehicles_per_km": float(
                                row["traffic_density_vehicles_per_km"]
                            ),
                            "congestion_level": congestion,
                        },
                    )

                    clear_live_traffic_cache(rds)
                    inserted += 1

                    print(
                        f"[{inserted}] {row['sensor_id']} | "
                        f"vehicles={row['vehicle_count']} | "
                        f"density={row['traffic_density_vehicles_per_km']} | "
                        f"congestion={congestion}"
                    )

                    if max_records and inserted >= max_records:
                        break

                    time.sleep(interval)

    finally:
        pg.close()
        rds.close()

    print(f"\nInserted {inserted} traffic readings into PostgreSQL.")
    print("Latest sensor readings were cached in Redis.")


if __name__ == "__main__":
    ingest()
