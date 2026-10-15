from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.database.models import TrafficRecord


def get_report_data(
    db: Session,
    range_name: str,
    start_date: date | None = None,
    end_date: date | None = None,
):
    range_name = range_name.lower()

    if range_name not in {"day", "week", "month"}:
        raise ValueError("range must be day, week, or month")

    latest_record = (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id != 4)
        .order_by(TrafficRecord.recorded_at.desc())
        .first()
    )

    if not latest_record:
        raise ValueError("No traffic data available")

    latest_time = latest_record.recorded_at

    if (start_date is None) != (end_date is None):
        raise ValueError("Both start_date and end_date must be supplied together.")

    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise ValueError("start_date must be on or before end_date.")
        start_time = datetime.combine(start_date, time.min)
        end_time = datetime.combine(end_date, time.max)
    else:
        if range_name == "day":
            start_time = latest_time - timedelta(days=1)
        elif range_name == "week":
            start_time = latest_time - timedelta(days=7)
        else:
            start_time = latest_time - timedelta(days=30)
        end_time = latest_time

    records = (
        db.query(TrafficRecord)
        .filter(
            TrafficRecord.road_id != 4,
            TrafficRecord.recorded_at >= start_time,
            TrafficRecord.recorded_at <= end_time,
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
