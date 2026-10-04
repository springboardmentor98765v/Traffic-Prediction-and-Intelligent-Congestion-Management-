from datetime import datetime

from pydantic import BaseModel


class ReportRow(BaseModel):
    road_id: int
    timestamp: datetime
    vehicle_count: float
    density: float
    congestion_level: str


class ReportResponse(BaseModel):
    range: str
    data: list[ReportRow]
