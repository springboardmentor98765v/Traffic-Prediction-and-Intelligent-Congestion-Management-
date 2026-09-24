from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    type: str = Field(..., description="Alert type: congestion, accident, closure, delay")
    severity: str = Field("medium", description="Alert severity: low, medium, high, critical")
    road_id: str = Field(..., description="Road identifier, e.g. R001, ROAD_01")
    message: str = Field(..., description="Human-readable alert message")
    target_role: Optional[str] = Field("public", description="Role visibility: public, operator, admin, all")
    source: Optional[str] = Field("system", description="Alert source: threshold_feed, anomaly_detector, road_condition, operator, system")


class AlertResponse(BaseModel):
    alert_id: str
    type: str
    severity: str
    road_id: str
    message: str
    read: bool = False
    created_at: datetime
    is_active: bool = True
    target_role: Optional[str] = "public"
    source: Optional[str] = "system"

    class Config:
        from_attributes = True


class AlertReadResponse(BaseModel):
    alert_id: str
    read: bool = True
    message: Optional[str] = "Alert marked as read"


class AlertCreateResponse(BaseModel):
    alert_id: str
    type: str
    severity: str
    road_id: str
    message: str
    created_at: datetime
    status: str = "created"


class AlertPollResponse(BaseModel):
    timestamp: str
    unread_count: int
    active_count: int
    alerts: List[AlertResponse]


class TriggerAlertsResponse(BaseModel):
    triggered_count: int
    alerts: List[AlertCreateResponse]
    details: dict
