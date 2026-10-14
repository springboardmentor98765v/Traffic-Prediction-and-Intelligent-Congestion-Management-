# Milestone 3 — AI/ML & Intelligent Routing Plan

## 1. Objective

The objective of Milestone 3 is to extend the existing AI/ML capabilities from Milestone 2 to support anomaly detection and AI-based traffic recommendations.

The AI/ML & Intelligent Routing component will:

- Detect traffic patterns that significantly deviate from expected or predicted congestion levels.
- Flag such anomalous patterns as possible traffic incidents.
- Use the existing M2 trained model along with historical traffic trend data for AI-based recommendations.
- Provide simple and explainable recommendations based on predicted congestion trends.
- Provide anomaly and recommendation information through APIs for integration with the Alert Service and other project components.

The implementation will focus on simple, explainable approaches using the existing M2 model and available historical trend data.


## 2. Existing M2 Model

Milestone 3 will build on the AI/ML model developed during Milestone 2.

The M2 AI Engine contains:

- A Random Forest Classifier for congestion-level prediction.
- A Random Forest Regressor for traffic-delay estimation.
- Feature engineering for traffic-related input variables.
- Prediction functionality for congestion level and estimated delay.
- Intelligent route ranking based on predicted traffic conditions.

The main traffic features used by the M2 model include:

- `hour_of_day`
- `day_of_week`
- `is_weekend`
- `is_rush_hour`
- `density`
- `vehicle_count`
- `rolling_avg_density`
- `rolling_avg_vehicle_count`

The existing M2 model will be reused instead of introducing a new complex ML model for Milestone 3.


## 3. Anomaly Detection Approach

The anomaly detection component will identify traffic conditions that differ significantly from the expected or predicted congestion level.

The basic approach is:

1. Obtain the observed traffic condition.
2. Use the M2 model to determine the expected congestion level.
3. Compare the observed level with the expected level.
4. Determine whether the difference is significant enough to be considered anomalous.
5. If an anomaly is detected, flag it as a possible traffic incident.

Example:

- Expected congestion level: `MEDIUM`
- Observed congestion level: `SEVERE`
- Result: Significant deviation detected.
- Flag: `possible_incident`

The initial implementation will use a simple and explainable threshold-based approach. The sensitivity of the detector can be tuned later using sample data and testing.


## 4. Accident/Incident Detection

The system will not directly claim that an accident has occurred.

Instead, unusual traffic behaviour will be treated as an indicator of a possible incident.

For example, if a road normally has a predicted congestion level of `LOW` or `MEDIUM`, but the observed traffic suddenly reaches `SEVERE`, the system can flag the road and time as a possible incident.

Expected output:

```text
road_id
time
expected_level
observed_level
flagged_as
## M3 Day 5 — Tuning & Validation

### Anomaly Detection Tuning

The anomaly detector was validated using all combinations of the four congestion levels:

- LOW
- MEDIUM
- HIGH
- SEVERE

The current anomaly threshold is based on the difference between expected and observed congestion levels.

```text
Anomaly condition:
observed_level - expected_level >= 2

## M3 Day 6 — Testing & Performance Validation

### Unit Testing

Anomaly detection and AI recommendation logic were tested using pytest.

Test coverage included:
- Medium → Severe anomaly detection
- Medium → High non-anomaly detection
- Low → Severe anomaly detection
- Same congestion level validation
- LOW traffic recommendation
- HIGH traffic recommendation
- SEVERE traffic recommendation
- Significant delay recommendation

### Test Result

- Total tests: 8
- Passed: 8
- Failed: 0

### Response Latency

The AI recommendation API was tested locally using the M3 recommendation endpoint.

Measured response time:
- Approximately 229 ms

### Day 6 Status

- Anomaly detection unit tests completed.
- Recommendation unit tests completed.
- All 8 tests passed successfully.
- Recommendation API response latency verified.
- No defects found in the tested anomaly and recommendation logic.