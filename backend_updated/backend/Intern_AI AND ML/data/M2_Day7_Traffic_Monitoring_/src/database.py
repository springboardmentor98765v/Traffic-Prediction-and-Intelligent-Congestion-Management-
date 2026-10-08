import os

import psycopg2

from dotenv import load_dotenv

# Load .env file
load_dotenv()


def get_postgres_connection():

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "traffic_monitoring"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "traffic123"),
    )
