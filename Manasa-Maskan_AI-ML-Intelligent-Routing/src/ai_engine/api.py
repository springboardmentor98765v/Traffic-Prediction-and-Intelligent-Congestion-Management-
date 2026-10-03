from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from .predictor import predict_traffic, get_traffic_condition
from .anomaly_detector import detect_anomalies
from .recommendation_engine import generate_recommendations

from ..route_analysis import (
    analyze_routes,
    get_best_route,
    get_travel_time,
    rank_routes_with_congestion,
)


# ---------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="TrafficVision AI Traffic Prediction API",
    description=(
        "API for traffic prediction, congestion forecasting, "
        "peak-hour analysis, delay estimation, intelligent "
        "route optimization and AI anomaly detection"
    ),
    version="3.0",
)


# ---------------------------------------------------------
# Input data structure
# ---------------------------------------------------------

class TrafficInput(BaseModel):
    road_id: int = Field(gt=0)
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "TrafficVision AI Traffic Prediction API is running",
        "version": "3.0",
        "status": "healthy",
    }


# ---------------------------------------------------------
# Basic Traffic Prediction
# ---------------------------------------------------------

@app.post("/predict")
def predict(data: TrafficInput):
    """
    Predict the number of vehicles and traffic condition.
    """

    prediction = predict_traffic(
        data.road_id,
        data.hour,
        data.day_of_week,
        data.month,
    )

    condition = get_traffic_condition(prediction)

    return {
        "road_id": data.road_id,
        "hour": data.hour,
        "day_of_week": data.day_of_week,
        "month": data.month,
        "predicted_vehicle_count": prediction,
        "traffic_condition": condition,
    }


# ---------------------------------------------------------
# M2 - Congestion Prediction
# ---------------------------------------------------------

@app.get("/predict/congestion")
def congestion_prediction(
    road_id: int = Query(gt=0),
    hour: int = Query(ge=0, le=23),
    day_of_week: int = Query(ge=0, le=6),
    month: int = Query(ge=1, le=12),
):
    """
    Predict traffic congestion for a road.
    """

    prediction = predict_traffic(
        road_id,
        hour,
        day_of_week,
        month,
    )

    condition = get_traffic_condition(prediction)

    return {
        "road_id": road_id,
        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "predicted_vehicle_count": prediction,
        "congestion_level": condition,
    }


# ---------------------------------------------------------
# M2 - Peak Hour Prediction
# ---------------------------------------------------------

@app.get("/predict/peak-hours")
def peak_hour_prediction(
    road_id: int = Query(gt=0),
    hour: int = Query(ge=0, le=23),
    day_of_week: int = Query(ge=0, le=6),
    month: int = Query(ge=1, le=12),
):
    """
    Identify whether the requested time is a peak traffic period.
    """

    prediction = predict_traffic(
        road_id,
        hour,
        day_of_week,
        month,
    )

    is_peak_hour = (
        7 <= hour <= 10
        or 17 <= hour <= 20
    )

    if 7 <= hour <= 10:
        peak_period = "Morning Peak"

    elif 17 <= hour <= 20:
        peak_period = "Evening Peak"

    else:
        peak_period = "Off-Peak"

    return {
        "road_id": road_id,
        "hour": hour,
        "predicted_vehicle_count": prediction,
        "is_peak_hour": is_peak_hour,
        "peak_period": peak_period,
    }


# ---------------------------------------------------------
# M2 - Delay Prediction
# ---------------------------------------------------------

@app.get("/predict/delay")
def delay_prediction(
    road_id: int = Query(gt=0),
    hour: int = Query(ge=0, le=23),
    day_of_week: int = Query(ge=0, le=6),
    month: int = Query(ge=1, le=12),
):
    """
    Estimate traffic delay category based on predicted traffic.
    """

    prediction = predict_traffic(
        road_id,
        hour,
        day_of_week,
        month,
    )

    condition = get_traffic_condition(prediction)

    if condition == "High Traffic":
        delay_category = "High Delay"
        estimated_delay_minutes = 15

    elif condition == "Medium Traffic":
        delay_category = "Medium Delay"
        estimated_delay_minutes = 8

    else:
        delay_category = "Low Delay"
        estimated_delay_minutes = 3

    return {
        "road_id": road_id,
        "hour": hour,
        "predicted_vehicle_count": prediction,
        "traffic_condition": condition,
        "delay_category": delay_category,
        "estimated_delay_minutes": estimated_delay_minutes,
    }


# ---------------------------------------------------------
# M3 - AI Anomaly Detection
# ---------------------------------------------------------

@app.get("/api/v1/ai/anomalies")
def ai_anomalies(
    max_results: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    """
    Detect unusual traffic patterns using the
    M2 trained model and historical traffic data.

    Anomalies are treated as possible incidents,
    not confirmed accidents.
    """

    result = detect_anomalies(
        threshold_std=2.0,
        max_results=max_results,
    )

    anomalies = []

    for anomaly in result["anomalies"]:
        anomalies.append(
            {
                "road_id": anomaly["road_id"],
                "time": anomaly["time"],
                "expected_level": anomaly["expected_level"],
                "observed_level": anomaly["observed_level"],
                "flagged_as": anomaly["flagged_as"],
            }
        )

    return anomalies


# ---------------------------------------------------------
# M3 - AI Recommendations
# ---------------------------------------------------------

@app.get("/api/v1/ai/recommendations")
def ai_recommendations(
    road_id: int = Query(gt=0),
):
    """
    Generate AI-based traffic recommendations
    for the specified road.
    """

    recommendations = generate_recommendations(
        road_id
    )

    return recommendations


# ---------------------------------------------------------
# M2 - Route Optimization
# ---------------------------------------------------------

@app.get("/route/optimize")
def route_optimization(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    junction_ids: list[int] = Query(
        ...,
        min_length=1,
    ),
    hour: int = Query(ge=0, le=23),
    day_of_week: int = Query(ge=0, le=6),
    month: int = Query(ge=1, le=12),
):
    """
    Return the best route using real map data
    and AI-predicted congestion.
    """

    routes = analyze_routes(
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
    )

    ranked_routes = rank_routes_with_congestion(
        routes,
        junction_ids,
        hour,
        day_of_week,
        month,
    )

    best_route = ranked_routes[0]

    return {
        "recommended_route": best_route,
        "routes": ranked_routes,
    }


# ---------------------------------------------------------
# M2 - Alternate Routes
# ---------------------------------------------------------

@app.get("/route/alternate")
def alternate_routes(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    junction_ids: list[int] = Query(
        ...,
        min_length=1,
    ),
    hour: int = Query(ge=0, le=23),
    day_of_week: int = Query(ge=0, le=6),
    month: int = Query(ge=1, le=12),
):
    """
    Return alternate routes ranked using
    AI-predicted congestion.
    """

    routes = analyze_routes(
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
    )

    ranked_routes = rank_routes_with_congestion(
        routes,
        junction_ids,
        hour,
        day_of_week,
        month,
    )

    return {
        "routes": ranked_routes,
    }


# ---------------------------------------------------------
# M2 - Travel Time Estimation
# ---------------------------------------------------------

@app.get("/route/travel-time")
def route_travel_time(
    route_id: str,
):
    """
    Return estimated travel time for a calculated route.
    """

    try:
        travel_time = get_travel_time(route_id)

        return travel_time

    except ValueError as error:
        return {
            "error": str(error)
        }


# ---------------------------------------------------------
# M2 - Road Conditions
# ---------------------------------------------------------

@app.get("/route/conditions")
def route_conditions(
    road_id: int = Query(gt=0),
):
    """
    Return road-condition information.

    Actual road-condition data will be connected
    from the Data Engineering / Traffic Monitoring module.
    """

    return {
        "road_id": road_id,
        "status": "Unknown",
        "notes": "Road-condition data not yet available.",
    }