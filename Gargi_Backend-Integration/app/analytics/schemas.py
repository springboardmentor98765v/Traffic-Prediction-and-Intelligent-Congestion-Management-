from datetime import datetime

from pydantic import BaseModel


class TrendPoint(BaseModel):
    timestamp: datetime
    vehicle_count: float
    density: float
    congestion_level: str
    average_speed_kmh: float | None = None


class TrendsResponse(BaseModel):
    road_id: int
    range: str
    data: list[TrendPoint]
