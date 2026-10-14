import csv
import psycopg
from pathlib import Path

# PostgreSQL details
DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "A"

# CSV file location
CSV_FILE = Path(__file__).parent.parent / "Data" / "traffic_dataset_1000_combined.csv"

# Connect to PostgreSQL
conn = psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

print("Connected to PostgreSQL!")

with conn.cursor() as cur:

    # Remove previous imported data
    cur.execute("TRUNCATE TABLE traffic_staging;")

    # Open CSV
    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        columns = [
            "reading_id",
            "source_record_id",
            "road_id",
            "road_code",
            "road_name",
            "road_description",
            "sensor_id",
            "sensor_code",
            "sensor_name",
            "sensor_type",
            "location",
            "status",
            "timestamp",
            "vehicle_count",
            "vehicle_capacity",
            "density",
            "congestion_level",
            "previous_congestion_level",
            "congestion_changed",
            "effective_from",
            "effective_to",
            "created_at"
        ]

        query = f"""
        INSERT INTO traffic_staging ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        """

        count = 0

        for row in reader:
            values = [row[column] or None for column in columns]
            cur.execute(query, values)
            count += 1

    conn.commit()

print(f"Imported {count} rows successfully!")

conn.close()
print("Done!")
