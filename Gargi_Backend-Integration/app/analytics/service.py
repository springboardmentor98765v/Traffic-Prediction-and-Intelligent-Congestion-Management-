from datetime import timedelta

from sqlalchemy.orm import Session

from app.database.models import TrafficRecord


def get_trends(
    db: Session,
    road_id: int,
    range_name: str,
):
    range_name = range_name.lower()

    if range_name not in {"day", "week"}:
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
    else:
        start_time = latest_time - timedelta(days=7)

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
            }
            for record in records
        ],
    }
