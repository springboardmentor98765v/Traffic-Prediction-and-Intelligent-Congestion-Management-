# TrafficVision AI — M3 Handoff Notes

## 1. Handoff Overview

This document summarizes the AI/ML and intelligent routing work
completed during Milestone 2 and the work recommended for Milestone 3.

**Owner:** Intern 3 — AI/ML & Intelligent Routing

---

## 2. Completed M2 Work

### Machine Learning Model

A Random Forest Classifier was trained for traffic congestion
classification.

- **Model version:** random-forest-v1
- **Algorithm:** Random Forest Classifier
- **Number of estimators:** 100
- **Maximum depth:** 8
- **Random state:** 42
- **Classes:** Low, Medium, High
- **Dataset:** `data/processed_traffic.csv`
- **Dataset size:** 840 rows
- **Train/test split:** 80/20
- **Training samples:** 672
- **Test samples:** 168

Model artifact:

`models/congestion_model.pkl`

---

## 3. Model Evaluation

The Random Forest model achieved:

- **Test accuracy:** 99.4%

Confusion matrix:

| Actual | High | Low | Medium |
|---|---:|---:|---:|
| High | 81 | 0 | 0 |
| Low | 0 | 23 | 1 |
| Medium | 0 | 0 | 63 |

The classification report and confusion matrix were generated in:

`notebook/day2_ml_model.ipynb`

---

## 4. Prediction Service

The AI/ML prediction service provides:

- `GET /api/v1/predict/congestion`
- `GET /api/v1/predict/peak-hours`
- `GET /api/v1/predict/delay`
- `GET /api/v1/predict/live`

The congestion endpoint loads the trained Random Forest model and
returns the predicted congestion level and confidence.

The service was tested locally on port `8001`.

---

## 5. Intelligent Routing

A congestion-aware route ranking component is available at:

`src/route_ranker.py`

The prototype considers:

- Distance
- Estimated delay
- Congestion penalty

Lower calculated scores are ranked first.

---

## 6. Testing Completed

### Model Testing

The Random Forest model was successfully loaded and used for direct
prediction.

Example:

- Road: `R001`
- Prediction: High
- Confidence: approximately 0.95
- Model version: `random-forest-v1`

### API Testing

The following endpoints were successfully tested:

- Congestion prediction
- Peak-hour prediction
- Delay estimation

### Latency Testing

A 100-prediction latency test was completed.

- **Total time:** approximately 0.247 seconds
- **Average latency:** approximately 2.47 ms/prediction
- **Status:** Passed

### Route Ranking Testing

The route ranking tests were executed successfully.

---

## 7. Integration Status

The AI/ML prediction service is operational and exposes prediction
APIs for integration.

The team Backend also has its own ML prediction implementation.

Therefore, the current successful API testing confirms that the
AI/ML service is operational, but it does not confirm that the team
Backend runtime is using this repository's
`congestion_model.pkl` artifact.

Frontend/backend integration with this specific model can be completed
after coordination with the respective team members.

---

## 8. Known Limitations

1. Current training data contains 840 processed records.
2. More representative traffic data is needed for real-world
   validation.
3. Density has a strong influence on the current congestion labels.
4. The current test accuracy should not be interpreted as guaranteed
   real-world performance.
5. Peak-hour prediction and delay estimation are currently based on
   service-level logic.
6. Weather and other external factors are not included in the current
   trained feature set.
7. The team Backend maintains a separate ML implementation.

---

## 9. M3 Recommended Tasks

### Data & Model

- Expand the traffic dataset.
- Validate the model on new/live observations.
- Investigate density dominance.
- Compare additional classification algorithms.
- Monitor Macro F1, precision, recall and other suitable metrics.

### Prediction

- Improve peak-hour forecasting.
- Improve delay estimation.
- Monitor model confidence and prediction performance.

### Routing

- Refine congestion-aware route scoring.
- Evaluate route rankings using realistic traffic scenarios.
- Continue coordination with the Route Analysis component.

### Engineering

- Maintain prediction endpoint tests.
- Continue latency testing.
- Maintain model versioning.
- Maintain dependency/version documentation.
- Coordinate model integration with the Backend and frontend teams.

---

## 10. Handoff Status

**M2 AI/ML work:** Completed

**Random Forest model:** Completed

**Prediction API:** Tested successfully

**Route ranking:** Tested successfully

**Latency testing:** Passed

**Model documentation:** Updated

**M3 handoff notes:** Updated

**Next focus:** Larger-data validation, model improvement, prediction
refinement, and routing enhancement.