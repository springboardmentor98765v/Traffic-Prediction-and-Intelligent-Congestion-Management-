"""
TrafficVision AI — Multi-Week Historical Data Generator (Milestone 2, Day 2)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Milestone 1's live simulator only produces a few hours of "now-ish"
    data. Real model training (Intern 3, starting Day 2) needs WEEKS of
    historical data with realistic patterns — not just rush hour, but
    weekday vs weekend differences too, since that's a genuinely
    learnable signal a model could pick up on.

    This script backfills the past N weeks directly into traffic_readings,
    at 5-minute intervals per road, using batch inserts for performance
    (avoids one-row-at-a-time inserts, which would be extremely slow at
    this volume).

Requirements:
    pip install psycopg2-binary

Run:
    python generate_historical_data.py
"""

import random
import time
from datetime import datetime, timedelta

import psycopg2
import psycopg2.extras

from congestion_logic import calculate_congestion_level, calculate_avg_speed

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "kitty@2211",  # <-- put your actual postgres password
}

WEEKS_OF_HISTORY = 4          # how many weeks back to generate
INTERVAL_MINUTES = 5          # one reading every 5 minutes, per road
BATCH_SIZE = 2000             # rows per batch insert (performance)

random.seed(7)  # reproducible historical dataset


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def fetch_roads(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT road_id, lanes FROM roads;")
        return cur.fetchall()  # list of (road_id, lanes)


def get_density_for_timestamp(ts: datetime) -> float:
    """
    Realistic-ish density generator factoring in BOTH:
      - hour of day (rush hour effect, same as Milestone 1)
      - day of week (weekday vs weekend — genuinely NEW for Milestone 2,
        since Milestone 1's simulator never varied by day)

    This gives Intern 3's model actual learnable signal beyond a flat
    rush-hour rule, per the M2 data documentation's recommendation.
    """
    hour = ts.hour
    weekday = ts.weekday()  # 0=Monday ... 6=Sunday
    is_weekend = weekday >= 5

    # Base density varies by hour (rush hour peaks)
    if hour in (8, 9, 18, 19):
        base = random.uniform(55, 90)
    elif hour in (7, 10, 17, 20):
        base = random.uniform(35, 60)
    elif 22 <= hour or hour <= 5:
        base = random.uniform(5, 20)  # late night, very light traffic
    else:
        base = random.uniform(20, 45)

    # Weekends are generally lighter, especially during "weekday rush" hours
    if is_weekend:
        base *= 0.6

    # Small random noise so it's not perfectly deterministic
    density = min(max(base + random.uniform(-5, 5), 0), 100)
    return round(density, 2)


def generate_rows(roads, weeks: int, interval_minutes: int):
    """
    Yields one row (as a tuple) at a time, working backward from now,
    for every road, at fixed intervals. Generator (not a big list) to
    keep memory usage sane even at tens of thousands of rows.
    """
    now = datetime.now()
    total_minutes = weeks * 7 * 24 * 60
    num_intervals = total_minutes // interval_minutes

    for i in range(num_intervals, 0, -1):
        ts = now - timedelta(minutes=i * interval_minutes)
        for road_id, lanes in roads:
            density = get_density_for_timestamp(ts)
            vehicle_count = int(density * lanes * random.uniform(3, 6))
            avg_speed = calculate_avg_speed(density)
            congestion_level = calculate_congestion_level(density)
            yield (road_id, road_id, vehicle_count, avg_speed, density, congestion_level, ts)


def insert_in_batches(conn, rows_generator, batch_size: int):
    total_inserted = 0
    batch = []

    insert_query = """
        INSERT INTO traffic_readings
            (road_id, sensor_id, vehicle_count, avg_speed_kmph, density, congestion_level, recorded_at)
        VALUES %s
    """

    with conn.cursor() as cur:
        for row in rows_generator:
            batch.append(row)
            if len(batch) >= batch_size:
                psycopg2.extras.execute_values(cur, insert_query, batch)
                conn.commit()
                total_inserted += len(batch)
                print(f"  Inserted {total_inserted} rows so far...")
                batch = []

        # insert any remaining rows smaller than one full batch
        if batch:
            psycopg2.extras.execute_values(cur, insert_query, batch)
            conn.commit()
            total_inserted += len(batch)

    return total_inserted


def main():
    print(f"Generating {WEEKS_OF_HISTORY} weeks of historical data, "
          f"{INTERVAL_MINUTES}-minute intervals...")

    conn = get_connection()
    try:
        roads = fetch_roads(conn)
        if not roads:
            print("No roads found — insert roads first (see Day 1/Day 2 setup).")
            return

        print(f"Found {len(roads)} road(s). Estimated rows: "
              f"~{(WEEKS_OF_HISTORY * 7 * 24 * 60 // INTERVAL_MINUTES) * len(roads)}")

        start_time = time.time()
        rows_gen = generate_rows(roads, WEEKS_OF_HISTORY, INTERVAL_MINUTES)
        total = insert_in_batches(conn, rows_gen, BATCH_SIZE)
        elapsed = time.time() - start_time

        print(f"\nDone. Inserted {total} historical rows in {elapsed:.1f} seconds.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
