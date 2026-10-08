import os

import psycopg2

from dotenv import load_dotenv

# Load .env file
load_dotenv()


def get_database_url():
    """
    DATABASE_URL (production, e.g. Neon with ?sslmode=require) as a libpq URL,
    or None so the POSTGRES_* settings below are used (local development).
    The SQLAlchemy driver suffix (postgresql+psycopg2://) is dropped for psycopg2.
    """

    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    return url.replace("postgresql+psycopg2://", "postgresql://", 1)


def get_postgres_connection():
    database_url = get_database_url()
    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "traffic_monitoring"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "traffic123"),
    )


def road_exists(road_id):
    """
    Check whether a road exists in the roads table.

    Returns:
        True  -> road exists
        False -> road does not exist
    """

    if not road_id:
        return False

    conn = get_postgres_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM roads
            WHERE road_id = %s
            LIMIT 1
            """,
            (road_id,),
        )

        return cursor.fetchone() is not None

    finally:
        conn.close()
