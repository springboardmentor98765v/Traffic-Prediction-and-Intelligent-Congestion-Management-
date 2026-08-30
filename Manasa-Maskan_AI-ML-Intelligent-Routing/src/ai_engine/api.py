from fastapi import FastAPI
from pydantic import BaseModel, Field
from .predictor import predict_traffic, get_traffic_condition
# Create FastAPI application
app = FastAPI(
    title="TrafficVision AI Traffic Prediction API",
    description="API for traffic prediction using Machine Learning",
    version="1.0"
)
# Input data structure
class TrafficInput(BaseModel):
    road_id: int = Field(gt=0)
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)
# Health check
@app.get("/")
def home():
    return {
        "message": "TrafficVision AI Traffic Prediction API is running"
    }
# Traffic prediction endpoint
@app.post("/predict")
def predict(data: TrafficInput):
    # Get vehicle count prediction
    prediction = predict_traffic(
        data.road_id,
        data.hour,
        data.day_of_week,
        data.month
    )
    # Get traffic condition
    condition = get_traffic_condition(prediction)
    # Return prediction result
    return {
        "road_id": data.road_id,
        "hour": data.hour,
        "day_of_week": data.day_of_week,
        "month": data.month,
        "predicted_vehicle_count": prediction,
        "traffic_condition": condition
    }