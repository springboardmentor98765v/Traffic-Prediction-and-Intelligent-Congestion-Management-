from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base  # Adjust this import if your Base class is imported differently

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, nullable=False)      # e.g., "congestion", "accident", "closure", "delay"
    severity = Column(String, nullable=False)  # e.g., "Low", "Medium", "High", "Critical"
    road_id = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)