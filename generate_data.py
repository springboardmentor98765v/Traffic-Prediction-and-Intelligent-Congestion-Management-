"""
TrafficVision AI — Synthetic Traffic Data Generator (Day 1)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Generates a small sample dataset that PRETENDS to be real traffic
    camera/sensor feed data. This unblocks Intern 3 (EDA) and gives
    everyone something concrete to look at before the live ingestion
    script (Day 2) exists.

Outputs:
    roads_sample.csv      -> list of road segments
    traffic_readings_sample.csv  -> synthetic time-series readings
    traffic_readings_sample.json -> same data, JSON format (for API mocking)
"""

import csv
import json
import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible sample data

# ---------------------------------------------------------
# 1. Sample roads (in a real project, replace with real road list)
# ---------------------------------------------------------
roads = [
    {"road_id": 1, "road_name": "Anna Salai",        "area": "Chennai Central", "road_type": "arterial", "length_km": 6.5, "lanes": 4},
    {"road_id": 2, "road_name": "OMR (IT Corridor)",  "area": "Sholinganallur", "road_type": "highway",  "length_km": 12.0, "lanes": 6},
    {"road_id": 3, "road_name": "Mount Road",          "area": "T. Nagar",       "road_type": "arterial", "length_km": 4.2, "lanes": 4},
    {"road_id": 4, "road_name": "GST Road",            "area": "Tambaram",       "road_type": "highway",  "length_km": 15.0, "lanes": 6},
    {"road_id": 5, "road_name": "Velachery Main Road",  "area": "Velachery",      "road_type": "local",    "length_km": 3.1, "lanes": 2},
]

def congestion_level(density):
    """Simple threshold rule — same style Intern 3 will use for the heuristic stub."""
    if density < 30:
        return "LOW"
    elif density < 60:
        return "MODERATE"
    elif density < 85:
        return "HIGH"
    else:
        return "SEVERE"

# ---------------------------------------------------------
# 2. Generate synthetic time-series readings
#    Simulates one reading every 5 minutes, for the last 2 hours, per road
# ---------------------------------------------------------
readings = []
reading_id = 1
now = datetime.now()

for road in roads:
    for i in range(24):  # 24 intervals x 5 min = 2 hours of history
        timestamp = now - timedelta(minutes=5 * (24 - i))

        # Simulate rush-hour effect: higher density around certain hours
        hour = timestamp.hour
        rush_factor = 1.4 if hour in (8, 9, 18, 19) else 1.0

        base_density = random.uniform(10, 70) * rush_factor
        density = min(round(base_density, 2), 100)
        vehicle_count = int(density * road["lanes"] * random.uniform(3, 6))
        avg_speed = round(max(5, 60 - density * 0.5 + random.uniform(-5, 5)), 1)

        readings.append({
            "reading_id": reading_id,
            "road_id": road["road_id"],
            "sensor_id": road["road_id"],  # 1 sensor per road for this sample
            "vehicle_count": vehicle_count,
            "avg_speed_kmph": avg_speed,
            "density": density,
            "congestion_level": congestion_level(density),
            "recorded_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        })
        reading_id += 1

# ---------------------------------------------------------
# 3. Write outputs
# ---------------------------------------------------------
with open("roads_sample.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=roads[0].keys())
    writer.writeheader()
    writer.writerows(roads)

with open("traffic_readings_sample.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=readings[0].keys())
    writer.writeheader()
    writer.writerows(readings)

with open("traffic_readings_sample.json", "w") as f:
    json.dump(readings, f, indent=2)

print(f"Generated {len(roads)} roads and {len(readings)} traffic readings.")
print("Files created: roads_sample.csv, traffic_readings_sample.csv, traffic_readings_sample.json")
