import csv
import os
import time
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from congestion_calculator import calculate_congestion
from redis_cache import (
    cache_latest_reading,
    get_redis_client,
    clear_live_traffic_cache,
)
load_dotenv()

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "traffic_monitoring_synthetic_dataset_with_density.csv"
)


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


def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv(
            "POSTGRES_DB",
            "traffic_monitoring"
        ),
        user=os.getenv(
            "POSTGRES_USER",
            "postgres"
        ),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def ingest(max_records=None):
    interval = float(
        os.getenv(
            "INGEST_INTERVAL_SECONDS",
            "5"
        )
    )

    inserted = 0

    pg = get_postgres_connection()
    rds = get_redis_client()

    try:
        with pg.cursor() as cur:
            with open(
                DATA_FILE,
                newline="",
                encoding="utf-8"
            ) as f:

                reader = csv.DictReader(f)

                for row in reader:

                    congestion = calculate_congestion(
                        int(row["vehicle_count"]),
                        int(row["road_capacity"])
                    )

                    values = (
                        row["road_id"],
                        row["sensor_id"],
                        row["timestamp"],
                        int(row["vehicle_count"]),
                        float(row["avg_speed_kmph"]),
                        int(row["road_capacity"]),
                        float(
                            row[
                                "traffic_density_vehicles_per_km"
                            ]
                        ),
                        congestion,
                        float(row["latitude"]),
                        float(row["longitude"]),
                    )

                    cur.execute(
                        INSERT_SQL,
                        values
                    )

                    pg.commit()

                    cache_latest_reading(
                        rds,
                        {
                            "road_id": row["road_id"],
                            "sensor_id": row["sensor_id"],
                            "timestamp": row["timestamp"],
                            "vehicle_count": int(
                                row["vehicle_count"]
                            ),
                            "avg_speed_kmph": float(
                                row["avg_speed_kmph"]
                            ),
                            "density_vehicles_per_km": float(
                                row[
                                    "traffic_density_vehicles_per_km"
                                ]
                            ),
                            "congestion_level": congestion,
                        }
                    )

                    clear_live_traffic_cache(rds)

                    inserted += 1

                    print(
                        f"[{inserted}] "
                        f"{row['sensor_id']} | "
                        f"vehicles="
                        f"{row['vehicle_count']} | "
                        f"density="
                        f"{row['traffic_density_vehicles_per_km']} | "
                        f"congestion="
                        f"{congestion}"
                    )

                    if (
                        max_records
                        and inserted >= max_records
                    ):
                        break

                    time.sleep(interval)

    finally:
        pg.close()
        rds.close()

    print(
        f"\nInserted {inserted} "
        "traffic readings into PostgreSQL."
    )

    print(
        "Latest sensor readings were "
        "cached in Redis."
    )


if __name__ == "__main__":
    ingest()