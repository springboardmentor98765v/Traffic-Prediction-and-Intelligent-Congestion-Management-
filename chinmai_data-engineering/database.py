import os

import psycopg2

from dotenv import load_dotenv


# Load .env file
load_dotenv()


def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv(
            "POSTGRES_HOST",
            "localhost"
        ),
        port=int(
            os.getenv(
                "POSTGRES_PORT",
                "5432"
            )
        ),
        dbname=os.getenv(
            "POSTGRES_DB",
            "traffic_monitoring"
        ),
        user=os.getenv(
            "POSTGRES_USER",
            "postgres"
        ),
        password=os.getenv(
            "POSTGRES_PASSWORD",
            "traffic123"
        ),
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
            (road_id,)
        )

        return cursor.fetchone() is not None

    finally:
        conn.close()