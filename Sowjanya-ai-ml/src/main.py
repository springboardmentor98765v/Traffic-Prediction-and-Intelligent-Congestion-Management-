from fastapi import FastAPI
from congestion_predictor import predict_congestion as get_prediction

app = FastAPI(title="TrafficVision AI Engine")


@app.get("/")
def home():
    return {"message": "TrafficVision AI Engine is running"}


@app.get("/api/v1/predict/congestion")
def predict_congestion(road_id: str, density: float, hour: int):

    prediction = get_prediction(density, hour)

    return {
        "road_id": road_id,
        "predicted_level": prediction,
        "confidence": 0.80,
        "generated_by": "heuristic-v0"
    }