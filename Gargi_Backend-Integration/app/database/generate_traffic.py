import random
from datetime import datetime, timezone, timedelta

from app.database.connection import SessionLocal
from app.database.models import TrafficRecord


def get_traffic_pattern(hour, road_id, weekday):
    base_vehicle_count = {
        1: 45,
        2: 60,
        3: 25,
    }[road_id]

    if 7 <= hour <= 10:
        multiplier = 1.6
    elif 17 <= hour <= 20:
        multiplier = 1.7
    elif 11 <= hour <= 16:
        multiplier = 1.2
    elif 21 <= hour <= 23:
        multiplier = 0.8
    else:
        multiplier = 0.5

    if weekday >= 5:
        multiplier *= 0.7

    noise = random.uniform(0.85, 1.15)

    vehicle_count = int(base_vehicle_count * multiplier * noise)

    capacity = {
        1: 100,
        2: 100,
        3: 80,
    }[road_id]

    density = vehicle_count / capacity
    density = min(max(density, 0.0), 1.0)

    if density >= 0.85:
        congestion_level = "HIGH"
    elif density >= 0.65:
        congestion_level = "MEDIUM"
    else:
        congestion_level = "LOW"

    # Synthetic demo estimate only; not a measured traffic speed.
    average_speed_kmh = round(
        max(5.0, min(60.0, 60.0 * (1.0 - density) + random.uniform(-3.0, 3.0))),
        1,
    )

    return vehicle_count, round(density, 2), congestion_level, average_speed_kmh


def generate_traffic_data():
    random.seed(42)

    db = SessionLocal()

    try:
        current_hour = datetime.now(timezone.utc).replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        start_time = current_hour - timedelta(days=7)

        records_created = 0

        for hour_index in range(7 * 24):
            timestamp = start_time + timedelta(hours=hour_index)

            weekday = timestamp.weekday()
            hour = timestamp.hour

            for road_id in [1, 2, 3]:
                existing_record = (
                    db.query(TrafficRecord)
                    .filter(
                        TrafficRecord.road_id == road_id,
                        TrafficRecord.recorded_at == timestamp,
                    )
                    .first()
                )

                if existing_record:
                    continue

                vehicle_count, density, congestion_level, average_speed_kmh = get_traffic_pattern(
                    hour,
                    road_id,
                    weekday,
                )

                record = TrafficRecord(
                    road_id=road_id,
                    vehicle_count=vehicle_count,
                    density=density,
                    congestion_level=congestion_level,
                    average_speed_kmh=average_speed_kmh,
                    recorded_at=timestamp,
                )

                db.add(record)
                records_created += 1

        db.commit()

        print(
            f"Historical traffic generation complete. "
            f"Records created: {records_created}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    generate_traffic_data()
