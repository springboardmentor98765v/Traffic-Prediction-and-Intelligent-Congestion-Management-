from datetime import datetime

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
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(500), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


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
    congestion_level = Column(String(50), nullable=False)

    recorded_at = Column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    road = relationship(
        "Road",
        back_populates="traffic_records",
    )
