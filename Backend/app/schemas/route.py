from pydantic import BaseModel, Field
from typing import List, Optional


class CoordinatePoint(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude")


class RouteOptimizeResponse(BaseModel):
    route_id: str
    path: List[List[float]] = Field(..., description="List of [latitude, longitude] pairs representing route geometry")
    distance_km: float = Field(..., description="Total distance in kilometers")
    congestion_score: float = Field(..., description="Calculated congestion score (lower is clearer)")
    summary: Optional[str] = Field(None, description="Human readable route summary")
    road_segments: Optional[List[str]] = Field(default_factory=list, description="Road IDs traversed")


class AlternateRouteItem(BaseModel):
    route_id: str
    path: List[List[float]] = Field(..., description="List of [latitude, longitude] pairs")
    distance_km: float
    congestion_score: float
    rank: int = Field(..., description="Rank from best to worst congestion/travel profile")
    recommendation_reason: Optional[str] = None


class TravelTimeResponse(BaseModel):
    route_id: str
    estimated_minutes: float = Field(..., description="Estimated travel time under current conditions")
    free_flow_minutes: Optional[float] = Field(None, description="Estimated travel time without traffic delay")
    delay_minutes: Optional[float] = Field(None, description="Estimated congestion delay in minutes")
    based_on: str = Field("live+predicted", description="Basis of estimation (e.g. live+predicted)")


class RoadConditionResponse(BaseModel):
    road_id: str
    status: str = Field(..., description="OPEN, CONSTRUCTION, CLOSED, HAZARD")
    notes: Optional[str] = None
    severity: Optional[str] = "Low"
    updated_at: Optional[str] = None


class RoadConditionUpdateRequest(BaseModel):
    road_id: str
    status: str
    notes: Optional[str] = None
    severity: Optional[str] = "Low"
