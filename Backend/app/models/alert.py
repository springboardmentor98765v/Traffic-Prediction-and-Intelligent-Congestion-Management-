import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class AlertType(str, enum.Enum):
    CONGESTION = "congestion"
    ACCIDENT = "accident"
    CLOSURE = "closure"
    DELAY = "delay"


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(30), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default=AlertSeverity.MEDIUM.value)
    road_id = Column(String(50), nullable=False, index=True)
    message = Column(String(500), nullable=False)
    target_role = Column(String(20), nullable=False, default="public", index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_read = Column(Boolean, nullable=False, default=False)
    source = Column(String(50), nullable=True, default="system")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reads = relationship("AlertRead", back_populates="alert", cascade="all, delete-orphan")


class AlertRead(Base):
    __tablename__ = "alert_reads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    read_at = Column(DateTime, default=datetime.utcnow)

    alert = relationship("Alert", back_populates="reads")
