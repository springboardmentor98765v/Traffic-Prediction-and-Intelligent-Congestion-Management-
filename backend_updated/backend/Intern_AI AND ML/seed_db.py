import os
import glob
import pandas as pd
from sqlalchemy import create_engine, text

DB_USER = "postgres"
DB_PASSWORD = "12345678"  # or check if your docker-compose password matches this
DB_HOST = "postgres"  # <-- Change from 127.0.0.1 to postgres
DB_PORT = "5432"
DB_NAME = "traffic_auth"

# 1. Ensure database exists
default_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
default_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")

try:
    with default_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"))
        if not result.scalar():
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"Database '{DB_NAME}' created successfully!")
except Exception as e:
    print(f"[ERROR] Could not verify/create database: {e}")

# 2. Connect to target database
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)


def seed_data():
    print("Searching for CSV files automatically...")
    roads_matches = glob.glob("**/road_conditions.csv", recursive=True)
    traffic_matches = glob.glob("**/historical_traffic_4weeks_cleaned.csv", recursive=True)

    roads_csv = roads_matches[0] if roads_matches else None
    traffic_csv = traffic_matches[0] if traffic_matches else None

    print(f"Found Roads CSV: {roads_csv}")
    print(f"Found Traffic CSV: {traffic_csv}")

    try:
        with engine.begin() as conn:
            # Ensure 'roads' table exists first to satisfy foreign keys
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS roads (
                    road_id VARCHAR(20) PRIMARY KEY,
                    road_name VARCHAR(100)
                );
            """))

        # 3. Seed Roads Table
        if roads_csv and os.path.exists(roads_csv):
            print("Reading road_conditions.csv...")
            df_roads = pd.read_csv(roads_csv)

            if "road_id" in df_roads.columns:
                roads_to_db = df_roads[["road_id"]].drop_duplicates()
                roads_to_db["road_name"] = roads_to_db["road_id"].apply(lambda x: f"Road {x}")
                print("Inserting into 'roads' table...")

                with engine.begin() as conn:
                    for _, row in roads_to_db.iterrows():
                        conn.execute(
                            text(
                                "INSERT INTO roads (road_id, road_name)"
                                " VALUES (:road_id, :road_name)"
                                " ON CONFLICT (road_id) DO NOTHING"
                            ),
                            {"road_id": row["road_id"], "road_name": row["road_name"]},
                        )
                print("Successfully seeded 'roads' table!")

        # 4. Seed Traffic History Table
        if traffic_csv and os.path.exists(traffic_csv):
            print("Reading historical_traffic_4weeks_cleaned.csv (this may take a few seconds)...")
            df_traffic = pd.read_csv(traffic_csv)
            print(f"Loaded {len(df_traffic)} rows. Inserting into database...")

            df_traffic.to_sql(
                "traffic_history",
                engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000,
            )
            print("Successfully seeded 'traffic_history' table!")

    except Exception as e:
        print(f"\n[ERROR] An exception occurred during seeding: {e}")


if __name__ == "__main__":
    seed_data()
