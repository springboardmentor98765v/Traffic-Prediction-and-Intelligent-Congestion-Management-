"""Generate four weeks of hourly simulated traffic history from the M1 road profiles."""

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_FILE = BASE_DIR / "data" / "traffic_monitoring_synthetic_dataset_with_density.csv"
OUTPUT_FILE = BASE_DIR / "data" / "historical_traffic_4weeks.csv"
WEEKS = 4
RANDOM_SEED = 42


def congestion_from_utilization(utilization: float) -> str:
    if utilization < 0.50:
        return "Low"
    if utilization <= 0.80:
        return "Medium"
    if utilization <= 1.00:
        return "High"
    return "Severe"


def load_profiles():
    grouped = {}
    with SOURCE_FILE.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            grouped.setdefault(row["road_id"], []).append(row)

    profiles = []
    for road_id, rows in sorted(grouped.items()):

        def mean(key):
            return sum(float(r[key]) for r in rows) / len(rows)

        first = rows[0]
        profiles.append(
            {
                "road_id": road_id,
                "road_name": first["road_name"],
                "sensor_id": first["sensor_id"],
                "road_capacity": int(first["road_capacity"]),
                "latitude": float(first["latitude"]),
                "longitude": float(first["longitude"]),
                "road_length_km": float(first["road_length_km"]),
                "base_vehicle_count": mean("vehicle_count"),
                "base_speed": mean("avg_speed_kmph"),
            }
        )
    return profiles


def traffic_factor(hour: int, weekday: int) -> float:
    if 7 <= hour <= 9:
        factor = 1.45
    elif 17 <= hour <= 20:
        factor = 1.55
    elif 0 <= hour <= 5:
        factor = 0.45
    elif 10 <= hour <= 16:
        factor = 0.90
    else:
        factor = 0.70
    if weekday >= 5:
        factor *= 0.82
    return factor * random.uniform(0.90, 1.10)


def generate():
    random.seed(RANDOM_SEED)
    profiles = load_profiles()
    if not profiles:
        raise RuntimeError("No road profiles found in the M1 dataset.")

    # Four complete weeks before the existing M1 sample period.
    start = datetime(2026, 7, 27, 0, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    end = start + timedelta(weeks=WEEKS)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "road_id",
        "road_name",
        "sensor_id",
        "timestamp",
        "vehicle_count",
        "avg_speed_kmph",
        "road_capacity",
        "congestion_level",
        "latitude",
        "longitude",
        "road_length_km",
        "traffic_density_vehicles_per_km",
        "source",
    ]

    count = 0
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        current = start
        while current < end:
            for p in profiles:
                factor = traffic_factor(current.hour, current.weekday())
                vehicles = max(
                    0, round(p["base_vehicle_count"] * factor * random.uniform(0.92, 1.08))
                )
                utilization = vehicles / p["road_capacity"]
                congestion = congestion_from_utilization(utilization)
                speed_factor = max(0.45, 1.0 - min(utilization, 1.5) * 0.35)
                speed = max(
                    5.0, round(p["base_speed"] * speed_factor * random.uniform(0.95, 1.05), 2)
                )
                density = round(vehicles / p["road_length_km"], 2)
                writer.writerow(
                    {
                        "road_id": p["road_id"],
                        "road_name": p["road_name"],
                        "sensor_id": p["sensor_id"],
                        "timestamp": current.isoformat(timespec="seconds"),
                        "vehicle_count": vehicles,
                        "avg_speed_kmph": speed,
                        "road_capacity": p["road_capacity"],
                        "congestion_level": congestion,
                        "latitude": p["latitude"],
                        "longitude": p["longitude"],
                        "road_length_km": p["road_length_km"],
                        "traffic_density_vehicles_per_km": density,
                        "source": "simulated_m2_day2",
                    }
                )
                count += 1
            current += timedelta(hours=1)

    print("=" * 60)
    print("M2 DAY 2 - HISTORICAL DATA GENERATION")
    print("=" * 60)
    print(f"Roads         : {len(profiles)}")
    print(f"Period        : {WEEKS} weeks")
    print("Interval      : 1 hour")
    print(f"Records       : {count}")
    print(f"Output        : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    generate()
