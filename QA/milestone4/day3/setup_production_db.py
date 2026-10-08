"""Milestone 4 Day 3 — create the schema and load the data into the production database.

    pip install psycopg2-binary pandas python-dotenv
    $env:DATABASE_URL="postgresql://...render.com/trafficvision?sslmode=require"  (PowerShell)
    python QA/milestone4/day3/setup_production_db.py --check   # read-only report first
    python QA/milestone4/day3/setup_production_db.py           # create/load what's missing

--check changes nothing: it compares the database with the schema the services query
(every table and column from the SQL files below) and prints row counts and the history
date range. Use it on a database someone else migrated (e.g. Intern 2's Render Postgres)
before writing to it.

Does what QA/milestone3/day6/analytics_setup.sh did for the local Docker DB, but over a
plain connection string, so it works against Render Postgres, Neon or any Postgres:

1. Analytics schema: roads + traffic_readings (database/schema.sql), then
   traffic_history / road_conditions / hourly + daily metrics and their indexes (sql/).
2. Data: roads and live readings from the synthetic dataset, the 4-week history,
   road conditions, then the hourly/daily aggregates.
3. ANALYZE + row counts.

Safe to re-run: DDL is IF NOT EXISTS and each table is only loaded when empty.
The backend creates its own tables (users, alerts) on startup.
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch

REPO = Path(__file__).resolve().parents[3]
ANALYTICS = REPO / "daa" / "M3_Day6_Traffic_Monitoring_"
sys.path.insert(0, str(ANALYTICS / "src"))

SCHEMA_FILES = [
    ANALYTICS / "database" / "schema.sql",
    ANALYTICS / "sql" / "milestone_2_schema.sql",
    ANALYTICS / "sql" / "m2_day5_aggregation.sql",
    ANALYTICS / "sql" / "m3_day5_analytics_optimization.sql",
]
LIVE_DATASET = ANALYTICS / "data" / "traffic_monitoring_synthetic_dataset_with_density.csv"


def connect():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL to the production connection string first.")
    return psycopg2.connect(url.replace("postgresql+psycopg2://", "postgresql://", 1))


def count(conn, table):
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {table}")
        return cur.fetchone()[0]


def apply_schema(conn):
    for path in SCHEMA_FILES:
        # psql meta-commands (\set ...) are not SQL; drop them.
        sql = "\n".join(
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("\\")
        )
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f"  applied {path.relative_to(REPO)}")


def load_roads_and_readings(conn):
    from congestion_calculator import calculate_congestion

    with LIVE_DATASET.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    roads = {}
    for row in rows:
        roads.setdefault(
            row["road_id"],
            (
                row["road_id"],
                row["road_name"],
                int(row["road_capacity"]),
                float(row["road_length_km"]),
                float(row["latitude"]),
                float(row["longitude"]),
            ),
        )
    with conn.cursor() as cur:
        execute_batch(
            cur,
            "INSERT INTO roads"
            " (road_id, road_name, road_capacity, road_length_km, latitude, longitude)"
            " VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (road_id) DO NOTHING",
            list(roads.values()),
        )
    conn.commit()
    print(f"  roads: {len(roads)} upserted")

    if count(conn, "traffic_readings"):
        print("  traffic_readings already loaded, skipping")
        return
    readings = [
        (
            row["road_id"],
            row["sensor_id"],
            row["timestamp"],
            int(row["vehicle_count"]),
            float(row["avg_speed_kmph"]),
            int(row["road_capacity"]),
            float(row["traffic_density_vehicles_per_km"]),
            # Same rule as the ingestion service (src/traffic_ingestion.py).
            calculate_congestion(int(row["vehicle_count"]), int(row["road_capacity"])),
            float(row["latitude"]),
            float(row["longitude"]),
        )
        for row in rows
    ]
    with conn.cursor() as cur:
        execute_batch(
            cur,
            "INSERT INTO traffic_readings (road_id, sensor_id, reading_timestamp, vehicle_count,"
            " avg_speed_kmph, road_capacity, traffic_density_vehicles_per_km, congestion_level,"
            " latitude, longitude) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            readings,
            page_size=500,
        )
    conn.commit()
    print(f"  traffic_readings: {len(readings)} loaded")


TABLE_RE = re.compile(r"CREATE TABLE IF NOT EXISTS (\w+)\s*\((.*?)\n\);", re.S | re.I)
NOT_COLUMNS = {"constraint", "primary", "unique", "check", "foreign"}


def expected_schema():
    """{table: [columns]} parsed from the CREATE TABLE statements the services rely on."""
    tables = {}
    for path in SCHEMA_FILES:
        for name, body in TABLE_RE.findall(path.read_text(encoding="utf-8")):
            cols = []
            for line in body.splitlines():
                word = line.strip().split(" ", 1)[0].strip('",')
                if word and word.lower() not in NOT_COLUMNS and re.fullmatch(r"\w+", word):
                    cols.append(word.lower())
            tables.setdefault(name.lower(), cols)
    return tables


def check(conn):
    """Read-only comparison of the live database with the expected schema."""
    problems = 0
    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        print(f"Server: {cur.fetchone()[0].split(',')[0]}\n")
        print(f"{'table':24} {'rows':>7}  status")
        for table, cols in expected_schema().items():
            cur.execute(
                "SELECT column_name FROM information_schema.columns"
                " WHERE table_schema = 'public' AND table_name = %s",
                (table,),
            )
            present = {row[0] for row in cur.fetchall()}
            if not present:
                print(f"{table:24} {'-':>7}  MISSING TABLE")
                problems += 1
                continue
            cur.execute(f"SELECT count(*) FROM {table}")
            rows = cur.fetchone()[0]
            missing = [c for c in cols if c not in present]
            status = "ok" if not missing else "missing columns: " + ", ".join(missing)
            if missing or rows == 0:
                problems += 1
            print(f"{table:24} {rows:>7}  {status if rows else status + ' (EMPTY)'}")
        cur.execute("SELECT to_regclass('public.traffic_history') IS NOT NULL")
        if cur.fetchone()[0]:
            cur.execute(
                "SELECT min(reading_timestamp), max(reading_timestamp) FROM traffic_history"
            )
            low, high = cur.fetchone()
            print(f"\ntraffic_history range: {low} -> {high}")
        for table in ("users", "alerts"):
            cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{table}",))
            note = "present" if cur.fetchone()[0] else "not yet (backend creates it on first start)"
            print(f"{table:24} {note}")
    print(f"\n{problems} problem(s). Fix them by running this script without --check.")
    return 1 if problems else 0


def run_loader(conn, table, module_name):
    if count(conn, table):
        print(f"  {table} already loaded, skipping")
        return
    module = __import__(module_name)
    module.main()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="read-only schema/data report")
    args = parser.parse_args()

    conn = connect()
    if args.check:
        try:
            return check(conn)
        finally:
            conn.close()
    try:
        print("1. Schema")
        apply_schema(conn)

        print("2. Data")
        load_roads_and_readings(conn)
        # Intern 2's loaders read DATABASE_URL through src/database.py / get_connection().
        run_loader(conn, "traffic_history", "load_historical_data")
        run_loader(conn, "road_conditions", "road_condition_ingestion")
        run_loader(conn, "hourly_traffic_metrics", "generate_traffic_aggregates")

        print("3. Verify")
        conn.commit()  # the count() checks above left a read transaction open
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("ANALYZE")
        tables = [
            "roads",
            "traffic_readings",
            "traffic_history",
            "road_conditions",
            "hourly_traffic_metrics",
            "daily_traffic_metrics",
        ]
        for table in tables:
            print(f"  {table:24} {count(conn, table):>6} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
