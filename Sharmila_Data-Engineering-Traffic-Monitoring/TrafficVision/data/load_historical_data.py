import pandas as pd
import psycopg2

# Read the generated CSV
df = pd.read_csv("traffic_history_4weeks.csv")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="trafficvision",
    user="postgres",
    password="sharmila0612"
)

cursor = conn.cursor()

# Insert each record
for _, row in df.iterrows():
    cursor.execute(
        """
        INSERT INTO traffic_history
        (road_id, timestamp, vehicle_count, density, congestion_level)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            int(row["road_id"]),
            row["timestamp"],
            int(row["vehicle_count"]),
            float(row["density"]),
            row["congestion_level"]
        )
    )

conn.commit()

cursor.close()
conn.close()

print(f"Successfully loaded {len(df)} records into traffic_history.")