"""
TrafficVision AI — Live Traffic Data Ingestion Simulator (Day 2)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Simulates a real-time traffic feed by writing a new reading for every
    road into the `traffic_readings` table every N seconds — like a
    real sensor/camera would, except the numbers are generated instead
    of coming from hardware.

    This unblocks:
      - Intern 3 (AI/ML): can query traffic_readings for live-ish data
      - Intern 4 (Frontend): dashboard can show data that keeps changing
      - Intern 5 (QA): can test the /traffic/live API against real DB rows

Requirements:
    pip install psycopg2-binary

Run:
    python ingest_live_data.py
    (Press Ctrl+C to stop)
"""

import time
import random
import sys
from datetime import datetime

import psycopg2

from congestion_logic import calculate_congestion_level, calculate_avg_speed

# ---------------------------------------------------------
# CONFIG — edit these to match your local setup
# ---------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "kitty@2211",   # <-- put your actual postgres password
}

INTERVAL_SECONDS = 5      # how often to insert a new reading per road
RUN_FOREVER = True        # set False + MAX_CYCLES if you want it to stop automatically
MAX_CYCLES = 20            # only used if RUN_FOREVER = False


def get_connection():
    """Open a connection to PostgreSQL. Exits with a clear message if it fails."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print("Could not connect to PostgreSQL. Check DB_CONFIG values above.")
        print(f"Details: {e}")
        sys.exit(1)


def fetch_roads(conn):
    """
    Get each road's id, lanes, AND its matching sensor_id by joining
    roads -> sensors. This avoids assuming sensor_id equals road_id,
    since sensor_id auto-increments independently.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT r.road_id, r.lanes, s.sensor_id
            FROM roads r
            JOIN sensors s ON s.road_id = r.road_id
            WHERE s.is_active = TRUE;
            """
        )
        rows = cur.fetchall()
    if not rows:
        print("No active sensors found. Make sure you've inserted rows into")
        print("BOTH 'roads' and 'sensors' tables before running this script.")
        sys.exit(1)
    return rows  # list of (road_id, lanes, sensor_id)


def get_rush_factor(hour: int) -> float:
    """
    Returns the rush-hour multiplier for a given hour (0-23).
    Pulled out as its own function (Day 6) so it can be unit tested
    directly, instead of being buried inline inside insert_reading().
    """
    return 1.4 if hour in (8, 9, 18, 19) else 1.0


def insert_reading(conn, road_id, lanes, sensor_id):
    """Generate one fake-but-realistic reading for a road and insert it."""
    hour = datetime.now().hour
    rush_factor = get_rush_factor(hour)

    density = round(min(random.uniform(10, 70) * rush_factor, 100), 2)
    vehicle_count = int(density * lanes * random.uniform(3, 6))
    avg_speed = calculate_avg_speed(density)
    congestion_level = calculate_congestion_level(density)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO traffic_readings
                (road_id, sensor_id, vehicle_count, avg_speed_kmph, density, congestion_level, recorded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (road_id, sensor_id, vehicle_count, avg_speed, density, congestion_level, datetime.now()),
        )
    conn.commit()
    return vehicle_count, density, congestion_level


def main():
    conn = get_connection()
    roads = fetch_roads(conn)
    print(f"Connected. Found {len(roads)} road(s). Starting live simulation...")
    print(f"Writing a new reading every {INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.\n")

    cycle = 0
    try:
        while True:
            cycle += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"--- Cycle {cycle} at {timestamp} ---")

            for road_id, lanes, sensor_id in roads:
                vehicle_count, density, level = insert_reading(conn, road_id, lanes, sensor_id)
                print(f"  road_id={road_id:<3} density={density:<6} vehicles={vehicle_count:<5} -> {level}")

            if not RUN_FOREVER and cycle >= MAX_CYCLES:
                print(f"\nReached MAX_CYCLES={MAX_CYCLES}, stopping.")
                break

            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
