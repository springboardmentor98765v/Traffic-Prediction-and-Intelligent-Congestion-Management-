from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    type: str
    severity: str
    road_id: int
    message: str


class AlertCreateResponse(BaseModel):
    alert_id: int


class AlertResponse(BaseModel):
    alert_id: int
    type: str
    severity: str
    road_id: int
    message: str
    read: bool
    created_at: datetime


class AlertReadResponse(BaseModel):
    alert_id: int
    read: bool
