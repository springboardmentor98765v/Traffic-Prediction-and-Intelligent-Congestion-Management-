import pandas as pd
import random
from datetime import datetime, timedelta

# Roads and sensors
roads = {
    "R001": "MG Road",
    "R002": "Ring Road",
    "R003": "Station Road",
    "R004": "Airport Road",
    "R005": "Civil Lines"
}

sensors = {
    "R001": "S001",
    "R002": "S002",
    "R003": "S003",
    "R004": "S004",
    "R005": "S005"
}

data = []

reading_id = 1

# Generate traffic readings for 7 days
start_time = datetime(2026, 8, 20, 0, 0)

for day in range(7):

    for hour in range(24):

        timestamp = start_time + timedelta(days=day, hours=hour)

        for road_id in roads:

            sensor_id = sensors[road_id]

            # Traffic pattern based on time of day
            if 7 <= hour <= 10:
                vehicle_count = random.randint(70, 140)
            elif 17 <= hour <= 20:
                vehicle_count = random.randint(80, 150)
            elif 11 <= hour <= 16:
                vehicle_count = random.randint(40, 90)
            else:
                vehicle_count = random.randint(10, 50)

            # Calculate density
            density = round(random.uniform(5, 90), 2)

            # Higher traffic generally means lower speed
            avg_speed = round(random.uniform(10, 60), 2)

            data.append([
                reading_id,
                road_id,
                sensor_id,
                timestamp,
                vehicle_count,
                avg_speed,
                density
            ])

            reading_id += 1

# Create DataFrame
columns = [
    "reading_id",
    "road_id",
    "sensor_id",
    "timestamp",
    "vehicle_count",
    "avg_speed",
    "density"
]

df = pd.DataFrame(data, columns=columns)

# Save dataset
df.to_csv("traffic_dataset.csv", index=False)

print("Dataset created successfully!")
print(f"Total records: {len(df)}")
print(df.head())