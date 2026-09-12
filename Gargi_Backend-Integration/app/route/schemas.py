from datetime import datetime

from pydantic import BaseModel


class RoutePathPoint(BaseModel):
    lat: float
    lng: float


class RouteResponse(BaseModel):
    route_id: str
    path: list[RoutePathPoint]
    distance_km: float
    duration_minutes: float
    congestion_score: float


class AlternateRouteResponse(BaseModel):
    route_id: str
    path: list[RoutePathPoint]
    distance_km: float
    duration_minutes: float
    congestion_score: float
    rank: int


class TravelTimeResponse(BaseModel):
    route_id: str
    estimated_minutes: float
    based_on: str


class RoadConditionResponse(BaseModel):
    road_id: int
    status: str
    notes: str | None
    updated_at: datetime
