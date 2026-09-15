from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class HistoricalTrafficRecord(BaseModel):
    road_id: str
    timestamp: str
    vehicle_count: int
    density: float
    congestion_level: str
    avg_speed: Optional[float] = None


class TrafficAggregateResponse(BaseModel):
    road_id: str
    granularity: str = Field(..., description="Aggregation interval: hour or day")
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_readings: int
    avg_density: float
    avg_vehicle_count: float
    avg_speed: float
    peak_hour: Optional[int] = None
    congestion_distribution: Dict[str, int] = Field(default_factory=dict)
