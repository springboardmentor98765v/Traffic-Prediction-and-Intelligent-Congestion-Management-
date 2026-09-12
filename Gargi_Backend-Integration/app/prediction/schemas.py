from pydantic import BaseModel


class CongestionPredictionResponse(BaseModel):
    road_id: int
    predicted_level: str
    confidence: float | None
    model_version: str


class PeakWindow(BaseModel):
    start: str
    end: str


class PeakHoursResponse(BaseModel):
    road_id: int
    peak_windows: list[PeakWindow]


class DelayResponse(BaseModel):
    road_id: int
    estimated_delay_minutes: float
    confidence: float
