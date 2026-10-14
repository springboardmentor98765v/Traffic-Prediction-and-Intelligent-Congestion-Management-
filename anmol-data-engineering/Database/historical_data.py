import psycopg
from pathlib import Path

# =========================================
# PostgreSQL Details
# =========================================

DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "A"


# =========================================
# Database Connection
# =========================================

def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# =========================================
# Load Historical Data
# =========================================

def load_historical_data():

    conn = get_connection()

    try:
        print("Connected to PostgreSQL!")

        with conn.cursor() as cur:

            # -----------------------------------------
            # Check available historical data
            # -----------------------------------------

            cur.execute("""
                SELECT
                    MIN(timestamp),
                    MAX(timestamp),
                    COUNT(*)
                FROM traffic_staging
                WHERE timestamp IS NOT NULL;
            """)

            start_time, end_time, staging_count = cur.fetchone()

            if start_time is None:
                raise Exception(
                    "No historical timestamp data found in traffic_staging."
                )

            print(f"Staging records : {staging_count}")
            print(f"Start time      : {start_time}")
            print(f"End time        : {end_time}")

            # -----------------------------------------
            # Load historical records
            # -----------------------------------------
            # The existing staging table already contains
            # the required processed traffic fields.
            #
            # ON CONFLICT prevents duplicate source records.
            # -----------------------------------------

            cur.execute("""
                INSERT INTO traffic_readings (
                    sensor_id,
                    source_record_id,
                    timestamp,
                    vehicle_count,
                    density,
                    congestion_level
                )
                SELECT
                    sensor_id,
                    source_record_id,
                    timestamp,
                    vehicle_count,
                    density,
                    congestion_level
                FROM traffic_staging
                WHERE timestamp IS NOT NULL
                AND sensor_id IS NOT NULL
                AND source_record_id IS NOT NULL
                AND vehicle_count IS NOT NULL
                AND density IS NOT NULL
                AND congestion_level IS NOT NULL
                ON CONFLICT (source_record_id)
                DO NOTHING;
            """)

            inserted_count = cur.rowcount

            conn.commit()

            print()
            print("=========================================")
            print("Historical Data Loading Completed")
            print("=========================================")
            print(f"Records inserted : {inserted_count}")
            print("Source           : traffic_staging")
            print("Destination      : traffic_readings")
            print("=========================================")

    except Exception as error:

        conn.rollback()

        print()
        print("Historical data loading failed.")
        print(f"Error: {error}")

    finally:
        conn.close()
        print("Database connection closed.")


# =========================================
# Program Entry Point
# =========================================

if __name__ == "__main__":
    load_historical_data()