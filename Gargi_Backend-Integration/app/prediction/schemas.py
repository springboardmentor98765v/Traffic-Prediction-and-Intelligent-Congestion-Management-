from pydantic import BaseModel


class PredictionResponse(BaseModel):
    road_id: int
    predicted_level: str
    confidence: float
    generated_by: str
