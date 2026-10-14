# TrafficVision AI Engine: Model Card & Milestone 3 Handoff

## 1. Model Overview
* **Model Version**: `model-v1` (Dual-Task Random Forest Pipeline)
* **Classifier Architecture**: `RandomForestClassifier(n_estimators=100, max_depth=10)`
* **Regressor Architecture**: `RandomForestRegressor(n_estimators=100, max_depth=10)`
* **Artifact Location**: `ai_engine/traffic_model_v2.joblib`
* **Features Used**: `hour_of_day`, `day_of_week`, `is_weekend`, `is_rush_hour`, `density`, `vehicle_count`, `rolling_avg_density`, `rolling_avg_vehicle_count`

---

## 2. Quantitative Evaluation Summary
* **Classification Accuracy**: 100% on 200 holdout test samples (20% split) across `LOW`, `MEDIUM`, `HIGH`, and `SEVERE`.
* **Delay Regression Metrics**:
  * Mean Absolute Error (MAE): 1.31 minutes
  * Root Mean Squared Error (RMSE): 1.63 minutes
  * Coefficient of Determination ($R^2$): 0.9586
  * Residual Mean (Bias): 0.172 minutes (demonstrating symmetric, unbiased errors)
* **Serving Latency**: Sub-50ms inference turn-around, well within the target ~1–2 second SLA.

---

## 3. Production API Contracts (Exposed to Intern 1 & Intern 4)

### 3.1 Congestion Level Inference
* `GET /predict/congestion?road_id={id}&density={val}&vehicle_count={val}&time={iso}`
* Returns qualitative tier, confidence score, and model signature.

### 3.2 Estimated Delay Calculation
* `GET /predict/delay?road_id={id}&density={val}&vehicle_count={val}&time={iso}`
* Returns continuous delay (minutes) and active rush-hour detection.

### 3.3 Rush Hour Window Diagnostics
* `GET /predict/peak-hours?hour={0-23}`
* Returns boolean flag for standard morning/evening traffic spikes.

### 3.4 Congestion-Aware Multi-Route Ranking
* `POST /predict/routes/rank`
* Accepts alternate route segment graphs from Intern 1, scores cumulative effective transit duration, and flags `rank: 1` (`is_recommended: true`).

---

## 4. Known Edge Cases & Mitigation
* **Severe Tier Support**: The initial dataset contains relatively fewer `SEVERE` instances (7 samples in holdout). Future retraining will benefit from synthetic oversampling.
* **Cold-Start Handling**: Unobserved segment IDs fallback to local momentary density and temporal heuristics without prior rolling history.

---

## 5. Milestone 3 Handoff & Service Bootstrap
* **FastAPI Service**: Launch via `uvicorn ai_engine.main:app --port 8000 --reload`
* **Readiness Probe**: `GET /health` returns `{ "status": "healthy", "model_loaded": true }`
* **Test Suite**: Run `python -m pytest tests/test_predict.py -v` (5/5 assertions green).


---

## 6. Milestone 3 AI Insights

### 6.1 Model Accuracy
- **Classification Accuracy:** 100% on 200 holdout test samples.
- All four congestion classes (`LOW`, `MEDIUM`, `HIGH`, `SEVERE`) were correctly classified in the evaluation set.
- **Observed false positives:** 0 in the 200-sample evaluation set.

### 6.2 Anomaly Detection
- An anomaly is flagged when the observed congestion level is at least two levels higher than the expected congestion level.
- Example: `MEDIUM → SEVERE` is flagged as a `possible_incident`.
- Normal deviations such as `MEDIUM → HIGH` are not flagged.
- The anomaly detector is a rule-based proxy for possible incidents and is not a dedicated accident classifier.

### 6.3 Recommendation Service
- AI recommendations are generated from predicted congestion level and estimated delay.
- Recommendations provide simple and explainable guidance such as travelling earlier, allowing additional travel time, or considering an alternate route.
- Local integration testing confirmed recommendation responses for both low- and severe-congestion scenarios.
- Historical trend integration was not available in the local test environment.

### 6.4 Limitations
- Model evaluation is based on a 200-sample holdout test set.
- The `SEVERE` class has limited representation in the evaluation set (7 samples).
- Anomaly detection uses congestion-level deviation rather than dedicated accident/incident classification.
- Full Alert Service integration could not be validated locally because the dependent Alert Service was not running on the AI service machine.
- Intern 2 historical trend data was not available during local recommendation testing.
- The reported 100% classification accuracy should therefore be interpreted within the evaluated test set rather than as a guarantee of real-world performance.

---

## 7. Milestone 4 Handoff

### Completed
- M2 Random Forest prediction pipeline retained and validated.
- M3 anomaly detection prototype and API implemented.
- M3 AI recommendation API implemented.
- Unit tests added for anomaly and recommendation logic.
- Response latency verified during M3 testing.
- M2 and M3 API regression checks performed locally.

### Handoff Notes
- AI service branch: `saksham-ai-ml`
- Anomaly endpoint: `GET /ai/anomalies`
- Recommendation endpoint: `GET /api/v1/ai/recommendations`
- Alert Service integration requires the shared Alert Service endpoint from Intern 1.
- Historical trend-based recommendations require the Analytics trend endpoint from Intern 2.