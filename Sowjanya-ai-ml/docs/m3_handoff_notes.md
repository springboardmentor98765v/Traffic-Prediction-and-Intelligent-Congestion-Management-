# TrafficVision AI — M3 Handoff Notes

## 1. Handoff Overview

This document summarizes the AI/ML work completed during Milestone 2
and the items to carry forward into Milestone 3.

**Owner:** Intern 3 — AI/ML & Intelligent Routing

---

## 2. Completed M2 Work

### Machine Learning Model

A Decision Tree Classifier was trained for traffic congestion
classification.

- **Model version:** model-v1
- **Algorithm:** Decision Tree Classifier
- **Classes:** Low, Medium, High
- **Dataset:** `data/processed_traffic.csv`
- **Dataset size:** 840 rows
- **Training/test split:** 80/20
- **Maximum tree depth:** 5
- **Random state:** 42

Model artifact:

`models/congestion_model.pkl`

---

## 3. Model Evaluation

The current model achieved:

- Test accuracy: **1.00**
- Precision: **1.00** for all classes
- Recall: **1.00** for all classes
- F1-score: **1.00** for all classes
- 5-fold cross-validation mean: **99.88%**
- Cross-validation standard deviation: approximately **0.24%**

Feature importance analysis showed:

- Density: **1.00**
- Other features: **0.00**

These results apply to the current processed dataset and should not
be interpreted as guaranteed real-world performance.

---

## 4. Prediction Service

The AI/ML service contains the following prediction endpoints:

- `GET /api/v1/predict/congestion`
- `GET /api/v1/predict/peak-hours`
- `GET /api/v1/predict/delay`
- `GET /api/v1/predict/live`

These provide congestion prediction, peak-hour information, delay
estimation, and live congestion predictions.

---

## 5. Intelligent Routing

A prototype congestion-aware route ranking component is available at:

`src/route_ranker.py`

The ranking logic considers:

- Distance
- Estimated delay
- Congestion penalty

Lower calculated scores are ranked first.

This is a prototype ranking approach and can be refined during M3.

---

## 6. Testing Completed

### ML Service Tests

The ML prediction service tests passed successfully.

### Route Ranking Tests

The route-ranking tests passed successfully.

### Latency Test

A 100-prediction latency test passed.

- Total time: approximately **0.247 seconds**
- Average latency: approximately **2.47 ms/prediction**

### Team Backend Integration

The team Backend was started successfully and tested through its
Swagger interface.

The following functionality was verified:

- Congestion prediction
- Peak-hour prediction
- Delay estimation
- Live prediction
- Congestion-aware alternate routing

Alternate routing was tested with:

- Origin: `R001`
- Destination: `R002`

The tested endpoints returned successfully.

---

## 7. Important Integration Note

The current team Backend contains its own ML prediction implementation.

The Backend ML service uses a Random Forest model and a separate
model artifact:

`congestion_model.joblib`

Therefore, the team's current Backend runtime model should not be
described as using the AI/ML repository's
`models/congestion_model.pkl` Decision Tree artifact unless a future
integration explicitly replaces or connects that artifact.

The Day 7 integration test verifies that the current team Backend
prediction and routing services are functioning; it does not by itself
prove that the Backend runtime is loading the AI/ML repository's
Decision Tree artifact.

---

## 8. Known Limitations

1. Current training data contains 840 processed records.
2. Density dominates the current Decision Tree feature importance.
3. Current high evaluation performance may reflect the relationship
   between the available features and labels in the dataset.
4. More representative traffic data is required for stronger
   real-world validation.
5. Peak-hour forecasting and delay estimation currently use service
   logic rather than separate trained forecasting/regression models.
6. Weather and other external traffic factors are not currently part
   of the trained feature set.
7. The team Backend currently uses a separate Random Forest model
   artifact.

---

## 9. M3 Handoff Tasks

The following work can be continued in Milestone 3:

### Data & Model

- Expand the traffic dataset.
- Validate the model using new/live observations.
- Investigate density dominance.
- Compare additional classification models.
- Track performance using Macro F1 and other suitable metrics.

### Prediction

- Improve peak-hour forecasting.
- Improve delay estimation using additional historical data.
- Monitor prediction confidence and model performance.

### Routing

- Refine congestion-aware route scoring.
- Evaluate route rankings using realistic traffic scenarios.
- Continue integration with the Route Analysis service.

### Engineering

- Maintain prediction endpoint tests.
- Continue latency testing.
- Monitor model compatibility with the Backend environment.
- Document model versions and dependencies.

---

## 10. Handoff Status

**Milestone 2 AI/ML work:** Completed

**Day 7 integration testing:** Passed

**Model documentation:** Updated

**M3 handoff documentation:** Prepared

**Next focus:** Model improvement, larger data validation,
prediction refinement, and routing enhancement.