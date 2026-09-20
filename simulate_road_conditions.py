"""
TrafficVision AI — Road Condition Simulator (Milestone 2, Day 4)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Milestone 1's road_conditions table (Day 1) only had every road
    seeded with a default CLEAR status — no real ingestion existed yet.
    This script simulates REAL-WORLD road condition events: some roads
    get construction, closures, or hazards, most stay clear — since in
    reality, most roads are fine most of the time, and only a few have
    active issues.

    Unlike ingest_live_data.py (which writes every 5 seconds forever),
    road conditions change much less often — so this is a one-shot
    "event" script, not a continuous loop. Run it whenever you want to
    simulate a new set of conditions (e.g. for a demo).

Requirements:
    pip install psycopg2-binary

Run:
    python simulate_road_conditions.py
"""

import random
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "kitty@2211",  # <-- put your actual postgres password
}

# Realistic condition scenarios — each with a status and a plausible note.
# CLEAR is intentionally the most common outcome, since most roads are
# fine most of the time in real life.
CONDITION_SCENARIOS = [
    ("CLEAR", "No known issues", 0.6),          # 60% chance
    ("CONSTRUCTION", "Lane closure for roadwork near junction", 0.15),
    ("HAZARD", "Pothole reported, exercise caution", 0.15),
    ("CLOSED", "Road closed due to accident cleanup", 0.10),
]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def fetch_roads(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT road_id, road_name FROM roads;")
        return cur.fetchall()


def pick_scenario():
    """Weighted random choice from CONDITION_SCENARIOS."""
    statuses, notes, weights = zip(*CONDITION_SCENARIOS)
    chosen_index = random.choices(range(len(statuses)), weights=weights, k=1)[0]
    return statuses[chosen_index], notes[chosen_index]


def insert_condition(conn, road_id, status, notes):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO road_conditions (road_id, status, notes, updated_at)
            VALUES (%s, %s, %s, NOW());
            """,
            (road_id, status, notes),
        )
    conn.commit()


def main():
    conn = get_connection()
    try:
        roads = fetch_roads(conn)
        if not roads:
            print("No roads found — make sure roads exist before running this.")
            return

        print(f"Simulating road conditions for {len(roads)} road(s)...\n")
        for road_id, road_name in roads:
            status, notes = pick_scenario()
            insert_condition(conn, road_id, status, notes)
            print(f"  {road_name} (road_id={road_id}): {status} — {notes}")

        print("\nDone. Each road now has a new condition entry "
              "(road_conditions keeps history — latest row = current status).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
