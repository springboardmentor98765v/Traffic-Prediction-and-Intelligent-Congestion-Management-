from app.database.connection import Base, SessionLocal, engine
from app.database.models import (
    Road,
    RoadCondition,
    Role,
    TrafficRecord,
)


def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        roles = ["admin", "operator", "public"]

        for role_name in roles:
            existing_role = db.query(Role).filter(Role.name == role_name).first()

            if not existing_role:
                db.add(Role(name=role_name))

        roads = [
            (1, "Anna Salai"),
            (2, "Mount Road"),
            (3, "GST Road"),
        ]

        for road_id, road_name in roads:
            existing_road = db.query(Road).filter(Road.id == road_id).first()

            if not existing_road:
                db.add(
                    Road(
                        id=road_id,
                        name=road_name,
                    )
                )

        db.commit()

        traffic_data = [
            (1, 42, 0.65, "MEDIUM"),
            (2, 75, 0.85, "HIGH"),
            (3, 20, 0.30, "LOW"),
        ]

        for road_id, vehicle_count, density, level in traffic_data:
            existing_record = (
                db.query(TrafficRecord).filter(TrafficRecord.road_id == road_id).first()
            )

            if not existing_record:
                db.add(
                    TrafficRecord(
                        road_id=road_id,
                        vehicle_count=vehicle_count,
                        density=density,
                        congestion_level=level,
                    )
                )

        db.commit()

    finally:
        db.close()
    conditions = [
        (
            1,
            "NORMAL",
            "Traffic flowing normally",
        ),
        (
            2,
            "CONGESTED",
            "Heavy traffic during peak hours",
        ),
        (
            3,
            "CLEAR",
            "Low traffic volume",
        ),
    ]

    for road_id, status, notes in conditions:
        existing_condition = (
            db.query(RoadCondition).filter(RoadCondition.road_id == road_id).first()
        )

        if not existing_condition:
            db.add(
                RoadCondition(
                    road_id=road_id,
                    status=status,
                    notes=notes,
                )
            )

    db.commit()


if __name__ == "__main__":
    seed_database()
