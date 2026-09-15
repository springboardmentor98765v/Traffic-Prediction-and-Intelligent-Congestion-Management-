from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CongestionPredictionResponse(BaseModel):
    road_id: str
    predicted_level: str = Field(..., description="Predicted congestion level: Low, Medium, High")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    model_version: str = Field("model-v1", description="Model version (e.g. model-v1)")
    generated_by: Optional[str] = Field("model-v1", description="Backward-compatible generator identifier")
    road_name: Optional[str] = None
    current_density: Optional[float] = None
    time_of_day: Optional[int] = None


class PeakWindow(BaseModel):
    start: str = Field(..., description="Start time in HH:MM format")
    end: str = Field(..., description="End time in HH:MM format")
    severity: Optional[str] = "High"


class PeakHoursResponse(BaseModel):
    road_id: str
    peak_windows: List[PeakWindow]


class DelayEstimateResponse(BaseModel):
    road_id: str
    estimated_delay_minutes: float = Field(..., description="Expected traffic delay in minutes")
    confidence: float = Field(..., ge=0.0, le=1.0)
    free_flow_speed_kmh: Optional[float] = None
    congested_speed_kmh: Optional[float] = None


class PredictionReportResponse(BaseModel):
    road_id: str
    road_name: str
    generated_at: str
    model_version: str
    current_level: str
    confidence: float
    estimated_delay_minutes: float
    peak_windows: List[PeakWindow]
    hourly_forecast: List[Dict[str, Any]]
