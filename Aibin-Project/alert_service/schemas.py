from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class AlertType(str, Enum):
    congestion = "congestion"
    accident = "accident"
    closure = "closure"
    delay = "delay"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class AlertCreate(BaseModel):
    type: AlertType
    severity: Severity
    road_id: str
    message: str

class AlertResponse(BaseModel):
    alert_id: int
    type: AlertType
    severity: Severity
    road_id: str
    message: str
    read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AlertReadResponse(BaseModel):
    alert_id: int
    read: bool
