from datetime import timedelta

from sqlalchemy.orm import Session

from app.database.models import TrafficRecord


def get_trends(
    db: Session,
    road_id: int,
    range_name: str,
):
    if road_id == 4:
        raise ValueError("Road 4 is not available.")

    range_name = range_name.lower()

    if range_name not in {"day", "week", "month"}:
        raise ValueError("range must be day or week")

    latest_record = (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id == road_id)
        .order_by(TrafficRecord.recorded_at.desc())
        .first()
    )

    if not latest_record:
        raise ValueError(
            f"No traffic data found for road {road_id}"
        )

    latest_time = latest_record.recorded_at

    if range_name == "day":
        start_time = latest_time - timedelta(days=1)
    elif range_name == "week":
        start_time = latest_time - timedelta(days=7)
    else:
        start_time = latest_time - timedelta(days=30)

    records = (
        db.query(TrafficRecord)
        .filter(
            TrafficRecord.road_id == road_id,
            TrafficRecord.recorded_at >= start_time,
            TrafficRecord.recorded_at <= latest_time,
        )
        .order_by(TrafficRecord.recorded_at.asc())
        .all()
    )

    return {
        "road_id": road_id,
        "range": range_name,
        "data": [
            {
                "timestamp": record.recorded_at,
                "vehicle_count": record.vehicle_count,
                "density": record.density,
                "congestion_level": record.congestion_level,
                "average_speed_kmh": record.average_speed_kmh if record.average_speed_kmh is not None else round(max(5.0, min(60.0, 60.0 * (1.0 - float(record.density or 0)))), 1),
                "average_speed_is_estimated": record.average_speed_kmh is None,
            }
            for record in records
        ],
    }
