import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, DateTime
from app.database.connection import Base


class RoadStatus(str, enum.Enum):
    OPEN = "OPEN"
    CONSTRUCTION = "CONSTRUCTION"
    CLOSED = "CLOSED"
    HAZARD = "HAZARD"


class RoadCondition(Base):
    __tablename__ = "road_conditions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    road_id = Column(String(20), unique=True, nullable=False, index=True)
    road_name = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default=RoadStatus.OPEN.value)
    notes = Column(String(500), nullable=True, default="Normal driving conditions")
    severity = Column(String(20), nullable=False, default="Low")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100), nullable=True, default="system")
