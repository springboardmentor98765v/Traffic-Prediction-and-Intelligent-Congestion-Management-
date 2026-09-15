# TrafficVision AI – M2 Handoff Notes

## 1. Module Owner

**Name:** Manasa Maskan

**Domain:** AI/ML + Intelligent Routing

**Project:** TrafficVision AI – Smart Traffic Prediction & Congestion Management System

---

## 2. M2 Work Completed

The following AI/ML and intelligent routing components were implemented:

- Traffic prediction model
- Feature engineering
- Model evaluation
- Model tuning
- Congestion prediction
- Peak-hour analysis
- Delay estimation
- Route optimization
- Alternative route calculation
- Route travel-time estimation
- Route condition analysis
- Congestion-aware route ranking
- FastAPI integration
- Automated testing

---

## 3. Important Files

### AI/ML

`src/train_m2_model.py`

Used to train the M2 traffic prediction model.

`src/evaluate_m2_model.py`

Used to evaluate the trained model.

`src/tune_m2_model.py`

Used to compare different Random Forest configurations.

`src/ai_engine/predictor.py`

Contains the traffic prediction and traffic condition logic.

`src/ai_engine/api.py`

Contains the FastAPI endpoints for the AI services.

---

## 4. Model Files

Production model:

`src/m2_traffic_model.pkl`

Tuned model:

`src/m2_traffic_model_tuned.pkl`

The original `m2_traffic_model.pkl` is currently used by
the prediction service.

---

## 5. Route and Map Files

`src/route_optimizer.py`

Ranks routes using predicted traffic and estimated delay.

`src/maps_service.py`

Connects the application to the OpenStreetMap/OSRM routing service.

`src/route_analysis.py`

Combines map route information with traffic prediction and
route analysis.

---

## 6. API Endpoints

The FastAPI application provides the following endpoints:

### Basic Prediction

`POST /predict`

Predicts vehicle count and traffic condition.

### Congestion Prediction

`GET /predict/congestion`

Predicts the congestion level for a selected junction and time.

### Peak-Hour Prediction

`GET /predict/peak-hours`

Identifies whether the selected time falls within a peak period.

### Delay Prediction

`GET /predict/delay`

Provides an estimated traffic delay category.

### Route Optimization

`GET /route/optimize`

Ranks available routes and identifies the recommended route.

### Alternative Routes

`GET /route/alternate`

Provides alternative routes between the selected origin
and destination.

### Route Travel Time

`GET /route/travel-time`

Returns the estimated travel time for a calculated route.

### Route Conditions

`GET /route/conditions`

Provides traffic-related information for a calculated route.

---

## 7. Map Routing Integration

The project uses OpenStreetMap-based OSRM routing.

The routing component provides:

- Route distance
- Estimated travel time
- Alternative routes
- Route geometry

The map routing service is combined with the AI traffic
prediction system to support intelligent route selection.

---

## 8. Model Performance

The production Random Forest model was evaluated using:

- Test samples: 9,624
- MAE: 8.21
- RMSE: 12.08

The model tuning process was also completed.

The tuned model achieved:

- Test MAE: 8.18
- Test RMSE: 12.17

The original model remains the production model.

---

## 9. Testing Status

Automated testing was completed using Pytest.

Test cases:

1. Traffic prediction
2. Traffic condition
3. Route analysis
4. Congestion route ranking

Final result:

`4 passed`

All four tests passed successfully.

---

## 10. Example Working Result

For the test input:

- Junction: 1
- Hour: 8
- Day of Week: 1
- Month: 11

The model produced:

- Predicted vehicles: 28.98
- Traffic condition: High Traffic

Example route analysis produced:

- Route 1: 3.22 km, 5.11 minutes
- Route 2: 3.26 km, 5.28 minutes

Congestion-aware ranking preferred Route 2 because its
predicted traffic was lower.

---

## 11. How to Start the API

Open the project terminal and activate the virtual environment.

Run:

```bash
python -m uvicorn src.ai_engine.api:app --reload