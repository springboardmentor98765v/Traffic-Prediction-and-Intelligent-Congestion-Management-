"""
TrafficVision AI — Database Parity Checker (Milestone 4)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Compares row counts (and a few sanity checks) between the LOCAL
    database and the PRODUCTION database, to confirm migration actually
    worked correctly. This is the tool behind the "data parity" check
    the SRS calls out for Day 4 — built now, on Day 1, since knowing
    exactly what will be verified later shapes the migration plan itself.

Requirements:
    pip install psycopg2-binary

Run:
    python check_db_parity.py
"""

import psycopg2

LOCAL_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "kitty@2211",
}

# Fill these in once the Day 2 cloud database actually exists
PRODUCTION_CONFIG = {
    "host": "YOUR_CLOUD_HOST_HERE",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "YOUR_CLOUD_USER_HERE",
    "password": "YOUR_CLOUD_PASSWORD_HERE",
}

TABLES_TO_CHECK = ["roads", "sensors", "traffic_readings", "road_conditions", "alert_thresholds"]


def get_row_counts(config):
    counts = {}
    conn = psycopg2.connect(**config)
    try:
        with conn.cursor() as cur:
            for table in TABLES_TO_CHECK:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    counts[table] = cur.fetchone()[0]
                except psycopg2.errors.UndefinedTable:
                    counts[table] = "TABLE MISSING"
                    conn.rollback()  # needed after an error to keep using the connection
    finally:
        conn.close()
    return counts


def main():
    print("Fetching row counts from LOCAL database...")
    local_counts = get_row_counts(LOCAL_CONFIG)

    print("Fetching row counts from PRODUCTION database...")
    try:
        prod_counts = get_row_counts(PRODUCTION_CONFIG)
    except psycopg2.OperationalError as e:
        print(f"\nCould not connect to production database: {e}")
        print("This is expected on Day 1 — fill in PRODUCTION_CONFIG once the cloud DB exists (Day 2).")
        return

    print("\n" + "=" * 55)
    print(f"{'TABLE':<20}{'LOCAL':<12}{'PRODUCTION':<12}{'MATCH'}")
    print("=" * 55)

    all_match = True
    for table in TABLES_TO_CHECK:
        local_count = local_counts.get(table, "N/A")
        prod_count = prod_counts.get(table, "N/A")
        match = "YES" if local_count == prod_count else "NO <-- MISMATCH"
        if match.startswith("NO"):
            all_match = False
        print(f"{table:<20}{str(local_count):<12}{str(prod_count):<12}{match}")

    print("=" * 55)
    if all_match:
        print("All tables match. Migration verified successfully.")
    else:
        print("MISMATCH FOUND — investigate before considering migration complete.")


if __name__ == "__main__":
    main()
