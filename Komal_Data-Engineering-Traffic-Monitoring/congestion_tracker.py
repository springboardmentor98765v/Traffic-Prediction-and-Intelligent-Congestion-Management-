import csv
from collections import defaultdict

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "processed_traffic.csv")


def track_congestion():
    congestion_history = defaultdict(list)

    with open(INPUT_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            road_id = row["road_id"]

            history_record = {
                "timestamp": row["timestamp"],
                "congestion": row["congestion"],
                "density": float(row["density"]),
                "avg_speed": float(row["avg_speed"])
            }

            congestion_history[road_id].append(history_record)

    return congestion_history


def show_congestion_history():
    history = track_congestion()

    print("\n===== CONGESTION HISTORY =====\n")

    for road_id, records in history.items():

        print(f"Road: {road_id}")

        for record in records:
            print(
                f"  Time: {record['timestamp']} | "
                f"Speed: {record['avg_speed']} | "
                f"Density: {record['density']} | "
                f"Congestion: {record['congestion']}"
            )

        print()


if __name__ == "__main__":
    show_congestion_history()
    