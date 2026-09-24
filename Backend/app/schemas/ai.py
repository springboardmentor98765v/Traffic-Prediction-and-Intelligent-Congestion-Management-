from typing import List, Optional
from pydantic import BaseModel, Field


class AnomalyItem(BaseModel):
    road_id: str = Field(..., description="Road identifier")
    time: str = Field(..., description="Timestamp or time bucket of anomaly")
    expected_level: str = Field(..., description="Expected congestion level from ML prediction")
    observed_level: str = Field(..., description="Observed/measured congestion level")
    flagged_as: str = Field("possible_incident", description="Flag classification")
    confidence: Optional[float] = Field(None, description="Confidence of the anomaly detection")
    severity: Optional[str] = Field("medium", description="Severity level: medium, high, critical")
    details: Optional[str] = Field(None, description="Explanation of anomalous pattern")


class RecommendationItem(BaseModel):
    recommendation_text: str = Field(..., description="Human-readable recommendation")
    based_on: str = Field(..., description="Data source or reasoning model")
    suggested_departure: Optional[str] = Field(None, description="Optimal departure time advice")
    alternate_route: Optional[str] = Field(None, description="Suggested alternative road")
    estimated_time_saving_minutes: Optional[int] = Field(None, description="Estimated time saved")
    confidence: Optional[float] = Field(None, description="Confidence score")
