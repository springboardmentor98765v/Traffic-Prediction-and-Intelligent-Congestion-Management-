from sqlalchemy.orm import Session

from app.database.models import RoadCondition


def get_road_condition(
    db: Session,
    road_id: int,
):
    condition = db.query(RoadCondition).filter(RoadCondition.road_id == road_id).first()

    if not condition:
        raise ValueError(f"No road condition found for road {road_id}")

    return {
        "road_id": condition.road_id,
        "status": condition.status,
        "notes": condition.notes,
        "updated_at": condition.updated_at,
    }
