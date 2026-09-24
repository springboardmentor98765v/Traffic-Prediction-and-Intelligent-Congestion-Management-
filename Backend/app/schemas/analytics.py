from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class TrendPoint(BaseModel):
    period: str = Field(..., description="Time bucket or day name (e.g. 08:00, Monday)")
    avg_congestion: float = Field(..., description="Average congestion level score (0.0 to 1.0 or scale)")
    avg_speed: Optional[float] = Field(None, description="Average vehicle speed in km/h")
    avg_density: Optional[float] = Field(None, description="Average vehicle density")
    congestion_label: Optional[str] = Field(None, description="Category: Low, Medium, High")


class TrafficTrendResponse(BaseModel):
    road_id: str
    range: str
    points: List[TrendPoint]
    summary: Optional[Dict[str, Any]] = None


class HeatmapResponse(BaseModel):
    range: str
    roads: List[str]
    road_names: Optional[List[str]] = None
    time_buckets: List[str]
    values: List[List[float]]


class HistoricalReportSummary(BaseModel):
    generated_at: str
    range: str
    total_records: int
    total_roads: int
    average_city_speed: float
    average_city_density: float
    high_congestion_incidents: int
    peak_congestion_road: str
    records: Optional[List[Dict[str, Any]]] = None
