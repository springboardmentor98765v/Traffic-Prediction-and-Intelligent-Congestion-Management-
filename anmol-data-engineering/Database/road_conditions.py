import psycopg

# PostgreSQL details
DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "A"


conn = psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

print("Connected to PostgreSQL!")

with conn.cursor() as cur:

    # Add sample road-condition data
    conditions = [
        (
            1,
            "CONSTRUCTION",
            "Road construction work in progress.",
            "2026-01-10 08:00:00",
            "2026-01-20 18:00:00"
        ),
        (
            2,
            "OPEN",
            "Road is open for normal traffic.",
            "2026-01-01 00:00:00",
            None
        ),
        (
            3,
            "CLOSED",
            "Road temporarily closed.",
            "2026-01-15 09:00:00",
            "2026-01-17 18:00:00"
        ),
        (
            4,
            "CONSTRUCTION",
            "Maintenance work in progress.",
            "2026-02-01 08:00:00",
            "2026-02-10 18:00:00"
        )
    ]

    query = """
        INSERT INTO road_conditions
        (
            road_id,
            condition_status,
            description,
            start_time,
            end_time
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    cur.executemany(query, conditions)

conn.commit()

print("Road-condition data added successfully!")

with conn.cursor() as cur:
    cur.execute("""
        SELECT
            condition_id,
            road_id,
            condition_status,
            description,
            start_time,
            end_time
        FROM road_conditions
        ORDER BY condition_id;
    """)

    rows = cur.fetchall()

    print("\nRoad Conditions:")
    for row in rows:
        print(row)

conn.close()

print("Database connection closed.")