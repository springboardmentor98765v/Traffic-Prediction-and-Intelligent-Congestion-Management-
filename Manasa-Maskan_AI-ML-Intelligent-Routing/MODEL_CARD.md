# TrafficVision AI – M2 Model Card

## 1. Model Overview

TrafficVision AI uses a Random Forest Regression model to predict the
number of vehicles on a road/junction.

The predicted vehicle count is then used to determine the traffic
condition and support intelligent route ranking.

---

## 2. Model Type

- Model: Random Forest Regressor
- Task: Traffic Volume Prediction
- Learning Type: Supervised Machine Learning
- Framework: Scikit-learn
- Number of Trees: 100
- Random State: 42

---

## 3. Dataset

The model was trained using the TrafficVision traffic dataset.

Dataset file:

`traffic.csv`

Dataset features:

- DateTime
- Junction
- Vehicles
- ID

The dataset contains 48,120 records.

---

## 4. Feature Engineering

The DateTime column was converted into useful time-based features.

The model uses the following input features:

- Junction
- Hour
- Day of Week
- Month

### Feature Description

| Feature | Description |
|---|---|
| Junction | Traffic junction identifier |
| Hour | Hour of the day from 0–23 |
| Day of Week | Day represented from 0–6 |
| Month | Month represented from 1–12 |

---

## 5. Target Variable

The target variable is:

`Vehicles`

It represents the number of vehicles observed at the junction.

---

## 6. Training and Testing

The dataset was divided into:

- 80% Training Data
- 20% Testing Data

Training samples:

38,496

Testing samples:

9,624

---

## 7. Model Performance

The trained Random Forest model was evaluated using:

### Mean Absolute Error (MAE)

`8.21`

### Root Mean Squared Error (RMSE)

`12.08`

The model was also tuned using different Random Forest configurations.

The tuned model achieved:

- Validation MAE: 8.34
- Validation RMSE: 12.41
- Final Test MAE: 8.18
- Final Test RMSE: 12.17

The original model is currently retained as the production model because
its overall RMSE performance was slightly better.

---

## 8. Traffic Condition Classification

The predicted vehicle count is converted into a traffic condition.

| Predicted Vehicles | Traffic Condition |
|---|---|
| Less than 10 | Low Traffic |
| 10–24.99 | Medium Traffic |
| 25 or more | High Traffic |

---

## 9. Prediction API

The model is integrated with FastAPI.

Main prediction endpoint:

`POST /predict`

M2 prediction endpoints:

`GET /predict/congestion`

`GET /predict/peak-hours`

`GET /predict/delay`

---

## 10. Route Optimization

Traffic predictions are used to rank possible routes.

The system considers:

- Predicted vehicle count
- Traffic condition
- Estimated delay
- Route distance
- Estimated travel time

The route with better traffic conditions and lower estimated delay
is ranked higher.

---

## 11. Map and Routing Integration

The system uses OpenStreetMap-based routing through OSRM.

The routing service provides:

- Route distance
- Estimated travel time
- Alternative routes
- Route geometry

The routing component is combined with the AI traffic prediction model
to support congestion-aware route selection.

---

## 12. Testing

Automated tests were created using Pytest.

The following tests were successfully executed:

- Traffic prediction test
- Traffic condition test
- Route analysis test
- Congestion route ranking test

Test result:

`4 passed`

---

## 13. Example Prediction

Example input:

- Junction: 1
- Hour: 8
- Day of Week: 1
- Month: 11

Example prediction:

- Predicted Vehicles: 28.98
- Traffic Condition: High Traffic

---

## 14. Example Route Ranking

Example routes:

| Route | Predicted Vehicles | Traffic | Delay |
|---|---:|---|---:|
| Route 2 | 9.61 | Low Traffic | 3 min |
| Route 1 | 28.98 | High Traffic | 15 min |

Based on these values, Route 2 is preferred.

---

## 15. Limitations

The current model uses historical traffic data and time-based
features.

The OSRM routing service provides road routing and travel-time
estimation but does not itself provide real-time traffic congestion.

Real-time traffic prediction can be improved in future versions by
integrating live traffic data with the machine learning model.

---

## 16. Future Improvements

Possible future improvements include:

- Integration of real-time traffic data
- More traffic-related features
- Improved congestion forecasting
- More advanced machine learning models
- Better travel-time estimation
- Integration with live map applications
- Continuous model retraining

---

## 17. Model Usage

The trained model is stored as:

`src/m2_traffic_model.pkl`

The prediction logic is implemented in:

`src/ai_engine/predictor.py`

The FastAPI service is implemented in:

`src/ai_engine/api.py`

Route optimization is implemented in:

`src/route_optimizer.py`

Map routing is implemented in:

`src/maps_service.py`

Route analysis is implemented in:

`src/route_analysis.py`