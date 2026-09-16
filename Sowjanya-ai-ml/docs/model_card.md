# TrafficVision AI — Model Card

## 1. Model Overview

- **Model name:** Traffic Congestion Classifier
- **Model version:** model-v1
- **Model type:** Decision Tree Classifier
- **Framework:** scikit-learn
- **Purpose:** Predict traffic congestion level for a road segment.
- **Prediction classes:** Low, Medium, High

The model is part of the AI/ML component of the TrafficVision AI
Smart Traffic Prediction & Congestion Management System.

---

## 2. Training Data

- **Dataset:** `data/processed_traffic.csv`
- **Number of rows:** 840
- **Number of columns:** 8
- **Missing values:** 0

### Input Features

The model uses:

1. `road_id_encoded`
2. `vehicle_count`
3. `avg_speed`
4. `density`
5. `hour`
6. `day_of_week`
7. `is_peak_hour`

---

## 3. Training Configuration

- **Algorithm:** Decision Tree Classifier
- **Maximum depth:** 5
- **Random state:** 42
- **Train/test split:** 80/20
- **Training samples:** 672
- **Test samples:** 168
- **Split strategy:** Stratified

The trained model is stored as:

`models/congestion_model.pkl`

---

## 4. Evaluation Results

### Test Set

- **Accuracy:** 1.00
- **Precision:** 1.00 for all classes
- **Recall:** 1.00 for all classes
- **F1-score:** 1.00 for all classes

### Cross-Validation

- **Method:** 5-fold cross-validation
- **Mean accuracy:** 99.88%
- **Standard deviation:** approximately 0.24%

### Feature Importance

- `density`: 1.00
- Other features: 0.00

The evaluation shows very strong performance on the current processed
dataset.

---

## 5. Prediction Service

The AI/ML service provides:

- `GET /api/v1/predict/congestion`
- `GET /api/v1/predict/peak-hours`
- `GET /api/v1/predict/delay`
- `GET /api/v1/predict/live`

The service returns congestion predictions and prediction confidence
where applicable.

---

## 6. Performance

Local prediction latency testing was completed successfully.

- **Test:** 100 predictions
- **Total time:** approximately 0.247 seconds
- **Average latency:** approximately 2.47 ms per prediction

This is below the project's target latency range of approximately
1–2 seconds for the service workflow.

---

## 7. Routing Component

A congestion-aware route ranking prototype is implemented in:

`src/route_ranker.py`

The prototype considers:

- Route distance
- Estimated delay
- Congestion penalty

Routes are sorted by the resulting score, with lower scores ranked
first.

---

## 8. Integration Testing

Milestone 2 Day 7 integration testing was completed successfully.

Verified through the team Backend Swagger interface:

- Backend startup
- Congestion prediction
- Peak-hour prediction
- Delay estimation
- Live congestion prediction
- Congestion-aware alternate route endpoint

The alternate-route endpoint was tested using:

- Origin: `R001`
- Destination: `R002`

All tested endpoints were working successfully.

---

## 9. Limitations

The current model has important limitations:

1. The dataset contains 840 processed records and may not represent
   all real-world traffic conditions.
2. `density` has complete feature importance in the current Decision
   Tree model.
3. The very high evaluation score should not be interpreted as
   guaranteed real-world accuracy.
4. More diverse and representative traffic data is required for
   stronger real-world validation.
5. Peak-hour forecasting and delay estimation currently include
   service-level logic and are not separate trained forecasting or
   regression models.
6. Weather and other external factors are not currently included in
   the trained feature set.

---

## 10. M3 Recommendations

For the next milestone:

- Collect a larger and more representative traffic dataset.
- Investigate the strong dependence of the model on density.
- Evaluate additional ML models.
- Monitor prediction performance on new/live data.
- Improve peak-hour forecasting.
- Improve delay estimation using additional historical data.
- Continue latency and integration testing.