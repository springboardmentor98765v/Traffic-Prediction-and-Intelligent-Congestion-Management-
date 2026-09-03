from sqlalchemy.orm import Session

from app.database.models import Road, TrafficRecord


def get_all_roads(db: Session):
    return db.query(Road).order_by(Road.id).all()


def get_road(
    db: Session,
    road_id: int,
):
    return db.query(Road).filter(Road.id == road_id).first()


def get_latest_traffic(
    db: Session,
    road_id: int,
):
    return (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id == road_id)
        .order_by(TrafficRecord.recorded_at.desc())
        .first()
    )


def get_traffic_history(
    db: Session,
    road_id: int,
):
    return (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id == road_id)
        .order_by(TrafficRecord.recorded_at.desc())
        .all()
    )


def create_traffic_record(
    db: Session,
    road_id: int,
    vehicle_count: int,
    density: float,
    congestion_level: str,
):
    record = TrafficRecord(
        road_id=road_id,
        vehicle_count=vehicle_count,
        density=density,
        congestion_level=congestion_level,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
