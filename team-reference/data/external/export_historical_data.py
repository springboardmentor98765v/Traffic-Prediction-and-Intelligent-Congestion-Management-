"""
TrafficVision AI — Export Real Historical Dataset for AI/ML Teammate
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Exports the ACTUAL traffic_readings data (the ~40,320-row historical
    dataset from generate_historical_data.py) to CSV — NOT the 120-row
    sample data (traffic_readings_sample.csv). This is Option B from
    her request: a CSV export she can drop directly into her AI/ML
    project instead of needing direct PostgreSQL access.

    Includes every column she asked for:
        Required: road_id, vehicle_count, avg_speed_kmph, density,
                   congestion_level, recorded_at
        Also included: reading_id, sensor_id, road_name, area,
                        road_type, length_km, lanes

Requirements:
    pip install psycopg2-binary

Run:
    python export_historical_data.py

Output:
    traffic_readings_export.csv   <- give this file to your AI/ML teammate
"""

import csv
import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "YOUR_PASSWORD_HERE",  # <-- put your actual postgres password
}

OUTPUT_FILE = "traffic_readings_export.csv"


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def export_data(conn):
    """
    Joins traffic_readings with roads to include road metadata
    (name, area, type, length, lanes) alongside every reading —
    exactly the combined column set she requested.
    """
    query = """
        SELECT
            tr.reading_id,
            tr.road_id,
            tr.sensor_id,
            tr.vehicle_count,
            tr.avg_speed_kmph,
            tr.density,
            tr.congestion_level,
            tr.recorded_at,
            r.road_name,
            r.area,
            r.road_type,
            r.length_km,
            r.lanes
        FROM traffic_readings tr
        JOIN roads r ON r.road_id = tr.road_id
        ORDER BY tr.road_id, tr.recorded_at ASC;
    """

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return rows


def write_csv(rows, output_file):
    if not rows:
        print("No rows found — is traffic_readings empty? Run generate_historical_data.py first.")
        return

    fieldnames = list(rows[0].keys())
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows):
    """
    Prints the exact summary she asked VS Code to report: row count,
    columns, unique roads, timestamp range, congestion-level distribution.
    """
    if not rows:
        return

    print("=" * 55)
    print("EXPORT SUMMARY")
    print("=" * 55)
    print(f"Row count: {len(rows)}")
    print(f"Columns: {list(rows[0].keys())}")

    unique_roads = sorted(set(r["road_id"] for r in rows))
    print(f"Unique roads: {unique_roads} ({len(unique_roads)} roads)")

    timestamps = [r["recorded_at"] for r in rows]
    print(f"Timestamp range: {min(timestamps)} to {max(timestamps)}")

    from collections import Counter
    level_counts = Counter(r["congestion_level"] for r in rows)
    print("Congestion-level distribution:")
    for level, count in level_counts.most_common():
        pct = count / len(rows) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")

    missing_density = sum(1 for r in rows if r["density"] is None)
    missing_speed = sum(1 for r in rows if r["avg_speed_kmph"] is None)
    print(f"Missing values — density: {missing_density}, avg_speed_kmph: {missing_speed}")


def main():
    print("Connecting to trafficvision database...")
    conn = get_connection()
    try:
        print("Exporting traffic_readings (joined with roads)...")
        rows = export_data(conn)

        write_csv(rows, OUTPUT_FILE)
        print(f"\nExported {len(rows)} rows to: {OUTPUT_FILE}")

        print()
        print_summary(rows)

        print("\n" + "=" * 55)
        print(f"DONE. Give '{OUTPUT_FILE}' to your AI/ML teammate.")
        print("This is the REAL historical dataset, NOT the sample CSV.")
        print("=" * 55)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
