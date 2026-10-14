"""
Pydantic schemas for Route Analysis Service.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")

class OptimizedRouteResponse(BaseModel):
    route_id: str = Field(..., description="Unique generated route identifier")
    path: List[List[float]] = Field(..., description="Ordered GPS coordinates [[lat, lng], ...]")
    distance_km: float = Field(..., description="Total driving distance in kilometers")
    congestion_score: float = Field(default=0.0, description="Congestion score (0.0 to 1.0) - placeholder in Day 1-3")
    summary: Optional[str] = Field(default=None, description="Corridor or road summary")

class RouteCandidate(BaseModel):
    route_id: str = Field(..., description="Unique generated route identifier")
    name: Optional[str] = Field(default=None, description="Descriptive route name")
    path: List[List[float]] = Field(..., description="Ordered GPS coordinates [[lat, lng], ...]")
    distance_km: float = Field(..., description="Total driving distance in kilometers")
    congestion_score: float = Field(default=0.0, description="Congestion score (0.0 to 1.0) - placeholder in Day 1-3")
    rank: int = Field(..., ge=1, description="Recommendation priority ranking (1 is best)")

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    maps_provider: str

# Day 4-5 Schemas (Documented for contract alignment)
class TravelTimeResponse(BaseModel):
    route_id: str = Field(..., description="Unique generated route identifier")
    estimated_minutes: float = Field(..., description="Estimated travel time in minutes")
    based_on: str = Field(..., description="Calculation basis ('distance' in Day 4, 'live+predicted' in Day 5)")
    baseline_minutes: Optional[float] = Field(default=None, description="Free-flow transit time")
    congestion_delay_minutes: Optional[float] = Field(default=None, description="Additional delay from traffic")

class RoadConditionsResponse(BaseModel):
    road_id: str = Field(..., description="Road corridor identifier")
    status: str = Field(..., description="Road condition status (e.g. 'OPEN', 'CONGESTED', 'CLEAR')")
    notes: str = Field(..., description="Description or condition details")
    current_density: Optional[float] = Field(default=None, description="Current traffic density")
    average_speed_kmh: Optional[float] = Field(default=None, description="Observed average vehicle speed")
