from datetime import datetime

from pydantic import BaseModel


class HeatmapPoint(BaseModel):
    road_id: int
    timestamp: datetime
    density: float
    vehicle_count: float
    congestion_level: str


class HeatmapResponse(BaseModel):
    range: str
    data: list[HeatmapPoint]
