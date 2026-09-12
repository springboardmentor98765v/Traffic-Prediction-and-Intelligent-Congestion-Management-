from datetime import datetime

from pydantic import BaseModel


class TrafficLiveResponse(BaseModel):
    road_id: int
    vehicle_count: int
    density: float
    congestion_level: str
    updated_at: datetime


class TrafficHistoryItem(BaseModel):
    road_id: int
    timestamp: datetime
    vehicle_count: int
    density: float
    congestion_level: str


class TrafficRoadResponse(BaseModel):
    road_id: int
    name: str
    congestion_level: str
    history: list[TrafficHistoryItem]


class TrafficDensityResponse(BaseModel):
    road_id: int
    density: float
    congestion_level: str


class TrafficAggregateItem(BaseModel):
    road_id: int
    period: str
    average_vehicle_count: float
    average_density: float
