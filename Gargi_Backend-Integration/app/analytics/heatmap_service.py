from datetime import timedelta

from sqlalchemy.orm import Session

from app.database.models import TrafficRecord


def get_heatmap(
    db: Session,
    range_name: str,
):
    range_name = range_name.lower()

    if range_name not in {"day", "week"}:
        raise ValueError("range must be day or week")

    latest_record = (
        db.query(TrafficRecord)
        .order_by(TrafficRecord.recorded_at.desc())
        .first()
    )

    if not latest_record:
        raise ValueError("No traffic data available")

    latest_time = latest_record.recorded_at

    if range_name == "day":
        start_time = latest_time - timedelta(days=1)
    else:
        start_time = latest_time - timedelta(days=7)

    records = (
        db.query(TrafficRecord)
        .filter(
            TrafficRecord.recorded_at >= start_time,
            TrafficRecord.recorded_at <= latest_time,
        )
        .order_by(
            TrafficRecord.recorded_at.asc(),
            TrafficRecord.road_id.asc(),
        )
        .all()
    )

    return {
        "range": range_name,
        "data": [
            {
                "road_id": record.road_id,
                "timestamp": record.recorded_at,
                "density": record.density,
                "vehicle_count": record.vehicle_count,
                "congestion_level": record.congestion_level,
            }
            for record in records
        ],
    }
