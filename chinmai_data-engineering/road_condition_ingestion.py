"""M2 Day 4 - Road-condition data ingestion."""

from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv

from database import get_postgres_connection


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "road_conditions.csv"

load_dotenv(BASE_DIR / ".env")

REQUIRED_COLUMNS = [
    "road_id",
    "condition_timestamp",
    "road_condition",
    "road_status",
    "incident_type",
    "description",
    "source",
]

VALID_STATUSES = {"Active", "Resolved", "Planned"}


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean road-condition records."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()
    df = df.dropna(subset=["road_id", "condition_timestamp", "road_condition", "road_status"])

    for column in ["road_id", "road_condition", "road_status", "incident_type", "description", "source"]:
        df[column] = df[column].fillna("").astype(str).str.strip()

    df["road_status"] = df["road_status"].str.title()

    invalid_statuses = set(df["road_status"]) - VALID_STATUSES
    if invalid_statuses:
        raise ValueError(f"Invalid road_status values: {invalid_statuses}")

    df["condition_timestamp"] = pd.to_datetime(
        df["condition_timestamp"], errors="coerce", utc=True
    )
    if df["condition_timestamp"].isna().any():
        raise ValueError("Invalid condition_timestamp values found.")

    before = len(df)
    df = df.drop_duplicates(
        subset=["road_id", "condition_timestamp", "road_condition", "road_status", "incident_type", "description"]
    )
    print(f"Duplicates removed: {before - len(df)}")

    return df


def validate_roads_exist(connection, df: pd.DataFrame) -> None:
    """Ensure every condition references an existing road."""
    road_ids = sorted(set(df["road_id"]))

    with connection.cursor() as cursor:
        cursor.execute("SELECT road_id FROM roads WHERE road_id = ANY(%s);", (road_ids,))
        existing = {row[0] for row in cursor.fetchall()}

    missing = sorted(set(road_ids) - existing)
    if missing:
        raise ValueError(f"Road IDs not found in roads table: {missing}")


def load_to_database(df: pd.DataFrame) -> int:
    """Load Day 4 records into PostgreSQL idempotently by source."""
    conn = get_postgres_connection()

    try:
        validate_roads_exist(conn, df)

        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM road_conditions WHERE source = %s;",
                ("simulated_m2_day4",),
            )

            for _, row in df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO road_conditions (
                        road_id,
                        condition_timestamp,
                        road_condition,
                        road_status,
                        incident_type,
                        description,
                        source
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        row["road_id"],
                        row["condition_timestamp"].to_pydatetime(),
                        row["road_condition"],
                        row["road_status"],
                        row["incident_type"] or None,
                        row["description"] or None,
                        row["source"] or "simulated_m2_day4",
                    ),
                )

        conn.commit()
        return len(df)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    print("=" * 60)
    print("M2 DAY 4 - ROAD CONDITION DATA INGESTION")
    print("=" * 60)

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Road-condition CSV not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)
    print(f"Input records: {len(df)}")

    cleaned = validate_data(df)
    print(f"Validated records: {len(cleaned)}")

    inserted = load_to_database(cleaned)
    print(f"Records loaded: {inserted}")
    print("Road-condition data successfully loaded into PostgreSQL.")
    print("=" * 60)


if __name__ == "__main__":
    main()
