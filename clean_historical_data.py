"""
TrafficVision AI — Historical Data Cleaning (Milestone 2, Day 3)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Before handing the historical dataset to Intern 3 for feature
    engineering, check for two common real-world data quality issues:

    1. DUPLICATES — the same road_id + recorded_at appearing more than
       once (could happen if a script is accidentally run twice, or a
       process retries after a timeout without checking if it already
       succeeded).
    2. GAPS — missing intervals where no reading exists for a stretch
       of time (could happen if the ingestion script was stopped, or a
       sensor "went offline").

    This script reports both, and safely removes duplicates (keeping
    the earliest one). Gaps are reported only, since they may be
    expected/acceptable depending on when scripts were actually running
    versus stopped.

Run:
    python clean_historical_data.py
"""

import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "kitty@2211",  # <-- put your actual postgres password
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def find_duplicates(conn):
    """
    Finds rows sharing the exact same (road_id, recorded_at) —
    these shouldn't exist, since each sensor reading should be unique
    at a given moment for a given road.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT road_id, recorded_at, COUNT(*) AS duplicate_count
            FROM traffic_readings
            GROUP BY road_id, recorded_at
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC;
            """
        )
        return cur.fetchall()


def remove_duplicates(conn):
    """
    Keeps the row with the LOWEST reading_id for each (road_id,
    recorded_at) pair, and deletes the rest. Uses a subquery with
    ROW_NUMBER() to identify which rows to keep vs delete.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH ranked AS (
                SELECT reading_id,
                       ROW_NUMBER() OVER (
                           PARTITION BY road_id, recorded_at
                           ORDER BY reading_id ASC
                       ) AS rn
                FROM traffic_readings
            )
            DELETE FROM traffic_readings
            WHERE reading_id IN (
                SELECT reading_id FROM ranked WHERE rn > 1
            );
            """
        )
        deleted_count = cur.rowcount
    conn.commit()
    return deleted_count


def find_gaps(conn, expected_interval_minutes=5, gap_threshold_minutes=15):
    """
    For each road, looks at consecutive readings and flags any gap
    bigger than gap_threshold_minutes (default: 3x the expected
    5-minute interval, to allow some normal jitter without false
    alarms).
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            WITH ordered AS (
                SELECT
                    road_id,
                    recorded_at,
                    LAG(recorded_at) OVER (PARTITION BY road_id ORDER BY recorded_at) AS prev_recorded_at
                FROM traffic_readings
            )
            SELECT
                road_id,
                prev_recorded_at,
                recorded_at,
                EXTRACT(EPOCH FROM (recorded_at - prev_recorded_at)) / 60 AS gap_minutes
            FROM ordered
            WHERE prev_recorded_at IS NOT NULL
              AND EXTRACT(EPOCH FROM (recorded_at - prev_recorded_at)) / 60 > %s
            ORDER BY gap_minutes DESC
            LIMIT 20;
            """,
            (gap_threshold_minutes,),
        )
        return cur.fetchall()


def main():
    conn = get_connection()
    try:
        print("=" * 55)
        print("STEP 1: Checking for duplicate readings...")
        print("=" * 55)
        duplicates = find_duplicates(conn)
        if duplicates:
            print(f"Found {len(duplicates)} duplicate group(s):")
            for d in duplicates[:10]:
                print(f"  road_id={d['road_id']} at {d['recorded_at']} -> {d['duplicate_count']} copies")
            deleted = remove_duplicates(conn)
            print(f"\nRemoved {deleted} duplicate row(s), kept the earliest of each.")
        else:
            print("No duplicates found. Dataset is clean on this front.")

        print("\n" + "=" * 55)
        print("STEP 2: Checking for gaps larger than 15 minutes...")
        print("=" * 55)
        gaps = find_gaps(conn)
        if gaps:
            print(f"Found {len(gaps)} gap(s) larger than 15 minutes (showing up to 20):")
            for g in gaps:
                print(f"  road_id={g['road_id']}: {g['gap_minutes']:.1f} min gap "
                      f"between {g['prev_recorded_at']} and {g['recorded_at']}")
            print("\nNote: gaps are reported, not auto-fixed — they may reflect real")
            print("periods when the ingestion script wasn't running, which is expected.")
        else:
            print("No significant gaps found.")

        print("\n" + "=" * 55)
        print("Data cleaning complete. Dataset ready for Intern 3.")
        print("=" * 55)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
