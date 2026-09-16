import csv
from collections import defaultdict


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "processed_traffic.csv")


def analyze_road_utilization():
    road_data = defaultdict(list)

    # Read processed traffic data
    with open(INPUT_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            road_data[row["road_id"]].append(row)

    results = []

    # Analyze each road
    for road_id, records in road_data.items():

        total_vehicles = sum(
            int(row["vehicle_count"])
            for row in records
        )

        average_speed = sum(
            float(row["avg_speed"])
            for row in records
        ) / len(records)

        average_density = sum(
            float(row["density"])
            for row in records
        ) / len(records)

        # Determine overall congestion
        high_count = sum(
            1 for row in records
            if row["congestion"] == "High"
        )

        medium_count = sum(
            1 for row in records
            if row["congestion"] == "Medium"
        )

        low_count = sum(
            1 for row in records
            if row["congestion"] == "Low"
        )

        if high_count >= medium_count and high_count >= low_count:
            overall_congestion = "High"

        elif medium_count >= low_count:
            overall_congestion = "Medium"

        else:
            overall_congestion = "Low"

        results.append({
            "road_id": road_id,
            "total_readings": len(records),
            "total_vehicles": total_vehicles,
            "average_speed": round(average_speed, 2),
            "average_density": round(average_density, 2),
            "congestion": overall_congestion
        })

    return results


if __name__ == "__main__":

    results = analyze_road_utilization()

    print("\n===== ROAD UTILIZATION ANALYSIS =====\n")

    for road in results:
        print(
            f"Road: {road['road_id']} | "
            f"Readings: {road['total_readings']} | "
            f"Vehicles: {road['total_vehicles']} | "
            f"Avg Speed: {road['average_speed']} | "
            f"Avg Density: {road['average_density']} | "
            f"Congestion: {road['congestion']}"
        )