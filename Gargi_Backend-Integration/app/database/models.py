from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    role = relationship("Role", back_populates="users")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(500), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)

    traffic_records = relationship(
        "TrafficRecord",
        back_populates="road",
        cascade="all, delete-orphan",
    )


class TrafficRecord(Base):
    __tablename__ = "traffic_records"

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(
        Integer,
        ForeignKey("roads.id"),
        nullable=False,
        index=True,
    )
    vehicle_count = Column(Integer, nullable=False)
    density = Column(Float, nullable=False)
    average_speed_kmh = Column(Float, nullable=True)
    congestion_level = Column(String(50), nullable=False)
    recorded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    road = relationship(
        "Road",
        back_populates="traffic_records",
    )


class RoadCondition(Base):
    __tablename__ = "road_conditions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    road_id = Column(
        Integer,
        ForeignKey("roads.id"),
        nullable=False,
        unique=True,
    )

    status = Column(
        String(50),
        nullable=False,
    )

    notes = Column(
        String(500),
        nullable=True,
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(
        String(50),
        nullable=False,
    )

    severity = Column(
        String(20),
        nullable=False,
    )

    road_id = Column(
        Integer,
        ForeignKey("roads.id"),
        nullable=False,
        index=True,
    )

    message = Column(
        String(500),
        nullable=False,
    )

    read = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    status = Column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    road = relationship("Road")

    recipients = relationship(
        "AlertRecipient",
        back_populates="alert",
        cascade="all, delete-orphan",
    )


class AlertRecipient(Base):
    __tablename__ = "alert_recipients"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    alert_id = Column(
        Integer,
        ForeignKey("alerts.id"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    read = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    alert = relationship("Alert")
    user = relationship("User")
