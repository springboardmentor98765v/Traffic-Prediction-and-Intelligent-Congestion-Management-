"""Load the M2 Day 2 historical CSV into PostgreSQL."""

import csv
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "historical_traffic_4weeks.csv"


def load_dotenv():
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_connection():
    load_dotenv()
    # Production (Neon): one DATABASE_URL instead of the POSTGRES_* parts.
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url.replace("postgresql+psycopg2://", "postgresql://", 1))
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "traffic_monitoring"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )


SQL = """
INSERT INTO traffic_history (
    road_id, sensor_id, reading_timestamp, vehicle_count, avg_speed_kmph,
    road_capacity, traffic_density_vehicles_per_km, congestion_level,
    latitude, longitude, source
) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(DATA_FILE)

    rows = []
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                (
                    row["road_id"],
                    row["sensor_id"],
                    row["timestamp"],
                    int(row["vehicle_count"]),
                    float(row["avg_speed_kmph"]),
                    int(row["road_capacity"]),
                    float(row["traffic_density_vehicles_per_km"]),
                    row["congestion_level"],
                    float(row["latitude"]),
                    float(row["longitude"]),
                    row["source"],
                )
            )

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(cur, SQL, rows, page_size=500)
        conn.commit()

    print("=" * 60)
    print("M2 DAY 2 - HISTORICAL DATA LOAD")
    print("=" * 60)
    print(f"Inserted records: {len(rows)}")
    print("Historical data successfully loaded.")
    print("=" * 60)


if __name__ == "__main__":
    main()
