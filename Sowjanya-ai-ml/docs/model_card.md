# TrafficVision AI — Model Card

## 1. Model Overview

- **Model name:** Traffic Congestion Classifier
- **Model version:** random-forest-v1
- **Model type:** Random Forest Classifier
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

The model uses the following engineered features:

1. `road_id_encoded`
2. `vehicle_count`
3. `avg_speed`
4. `density`
5. `hour`
6. `day_of_week`
7. `is_peak_hour`

### Target

- `congestion`
- Classes: Low, Medium, High

---

## 3. Training Configuration

- **Algorithm:** Random Forest Classifier
- **Number of estimators:** 100
- **Maximum depth:** 8
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

The Random Forest model achieved:

- **Test accuracy:** 99.4%

The detailed precision, recall and F1-score values are reported in
the ML notebook.

### Confusion Matrix

The confusion matrix was generated using the held-out test dataset.

The observed test predictions were:

| Actual | Predicted High | Predicted Low | Predicted Medium |
|---|---:|---:|---:|
| High | 81 | 0 | 0 |
| Low | 0 | 23 | 1 |
| Medium | 0 | 0 | 63 |

This indicates that one Low-congestion sample was classified as
Medium in the test set.

---

## 5. Prediction Service

The AI/ML service provides the following endpoints:

- `GET /api/v1/predict/congestion`
- `GET /api/v1/predict/peak-hours`
- `GET /api/v1/predict/delay`
- `GET /api/v1/predict/live`

The congestion prediction endpoint uses the trained Random Forest
model and returns the predicted congestion level and confidence.

---

## 6. Example Prediction

For a test prediction on road `R001`, the Random Forest service
successfully returned:

- **Predicted level:** High
- **Confidence:** approximately 0.95
- **Model version:** `random-forest-v1`

Prediction values may vary depending on the input traffic conditions.

---

## 7. Performance

A local latency test was performed using 100 predictions.

- **Total time:** approximately 0.247 seconds
- **Average latency:** approximately 2.47 ms per prediction
- **Latency test:** Passed

---

## 8. Intelligent Routing

A congestion-aware route ranking prototype is implemented in:

`src/route_ranker.py`

The ranking logic considers:

- Route distance
- Estimated delay
- Congestion penalty

Routes are sorted by the resulting score, with lower scores ranked
first.

---

## 9. Integration Testing

The AI/ML service was successfully started and tested through its
Swagger interface.

Verified functionality includes:

- Congestion prediction
- Peak-hour prediction
- Delay estimation
- Model loading
- Random Forest prediction
- Prediction confidence

The team Backend prediction API was also tested separately.

The team Backend currently has its own prediction implementation, so
the successful Backend response should not be interpreted as proof
that it is loading this `congestion_model.pkl` artifact.

---

## 10. Limitations

1. The current dataset contains 840 processed records.
2. The dataset may not represent all real-world traffic conditions.
3. Density has a strong relationship with the congestion labels.
4. High test accuracy should not be interpreted as guaranteed
   real-world accuracy.
5. More diverse and representative traffic data is required for
   stronger validation.
6. Peak-hour forecasting and delay estimation currently include
   service-level logic rather than separate trained forecasting and
   regression models.
7. Weather and other external traffic factors are not currently
   included in the trained feature set.
8. The team Backend currently maintains a separate ML implementation.

---

## 11. Future Improvements

- Expand the traffic dataset.
- Validate the model using new/live traffic observations.
- Compare additional ML algorithms.
- Monitor model performance on unseen data.
- Improve peak-hour forecasting.
- Improve delay estimation.
- Add additional traffic and environmental features.
- Continue integration and latency testing.