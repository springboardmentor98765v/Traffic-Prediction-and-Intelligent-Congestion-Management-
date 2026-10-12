from datetime import timedelta

from sqlalchemy.orm import Session

from app.database.models import TrafficRecord


def get_report_data(
    db: Session,
    range_name: str,
):
    range_name = range_name.lower()

    if range_name not in {"day", "week", "month"}:
        raise ValueError("range must be day or week")

    latest_record = (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id != 4)
        .order_by(TrafficRecord.recorded_at.desc())
        .first()
    )

    if not latest_record:
        raise ValueError("No traffic data available")

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
            TrafficRecord.road_id != 4,
            TrafficRecord.recorded_at >= start_time,
            TrafficRecord.recorded_at <= latest_time,
        )
        .order_by(
            TrafficRecord.recorded_at.asc(),
            TrafficRecord.road_id.asc(),
        )
        .all()
    )

    return [
        {
            "road_id": record.road_id,
            "timestamp": record.recorded_at,
            "vehicle_count": record.vehicle_count,
            "density": record.density,
            "congestion_level": record.congestion_level,
        }
        for record in records
    ]
