import pandas as pd
import numpy as np

# Reproducible results
np.random.seed(42)

# Configuration
roads = [1, 2, 3, 4]
start_time = "2026-01-01 00:00:00"
weeks = 4

# Generate hourly timestamps for 4 weeks
timestamps = pd.date_range(
    start=start_time,
    periods=weeks * 7 * 24,
    freq="h"
)

records = []

for road_id in roads:
    for timestamp in timestamps:

        hour = timestamp.hour
        weekday = timestamp.weekday()

        # Base traffic
        base_vehicles = np.random.randint(20, 80)

        # Morning and evening peak hours
        if 7 <= hour <= 9:
            base_vehicles += np.random.randint(30, 60)

        elif 17 <= hour <= 20:
            base_vehicles += np.random.randint(40, 70)

        # Slightly lower traffic on weekends
        if weekday >= 5:
            base_vehicles = int(base_vehicles * 0.75)

        vehicle_count = max(1, base_vehicles)

        # Simulated traffic density
        density = round(vehicle_count / 100, 3)

        # Congestion classification
        if density < 0.4:
            congestion_level = "Low"
        elif density < 0.7:
            congestion_level = "Medium"
        else:
            congestion_level = "High"

        records.append([
            road_id,
            timestamp,
            vehicle_count,
            density,
            congestion_level
        ])

# Create DataFrame
df = pd.DataFrame(
    records,
    columns=[
        "road_id",
        "timestamp",
        "vehicle_count",
        "density",
        "congestion_level"
    ]
)

# Save dataset
output_file = "traffic_history_4weeks.csv"
df.to_csv(output_file, index=False)

print("Historical dataset generated successfully!")
print(f"Records: {len(df)}")
print(f"Roads: {df['road_id'].nunique()}")
print(f"Start: {df['timestamp'].min()}")
print(f"End: {df['timestamp'].max()}")
print(f"Saved to: {output_file}")