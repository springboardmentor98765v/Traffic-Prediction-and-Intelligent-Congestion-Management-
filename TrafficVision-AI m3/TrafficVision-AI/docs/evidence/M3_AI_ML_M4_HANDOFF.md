# TrafficVision AI — M3 AI/ML to M4 Handoff Notes

**Role:** Intern 3 — AI/ML  
**Milestone:** M3 — Alerts, Analytics & AI Insights  
**Handoff:** M3 → M4  
**Project:** AI-Powered Traffic Prediction and Intelligent Congestion Management Platform

---

# 1. M3 AI/ML Responsibility

The M3 AI/ML scope covered:

1. Anomaly / possible-incident detection
2. AI-based traffic recommendations
3. Integration with the M2 trained congestion prediction model
4. Integration with historical traffic data from Intern 2
5. AI/ML testing, API validation, and performance checks

The primary objective was to extend the M2 traffic prediction capabilities with AI-driven detection of unusual traffic behavior and road-specific traffic recommendations.

---

# 2. M3 AI/ML Architecture

The M3 AI/ML flow is:

```text
                    HISTORICAL TRAFFIC DATA
                              |
                              v
                    HISTORICAL BASELINE
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
      ANOMALY DETECTION                TRAFFIC TRENDS
             |                                 |
             v                                 v
   Traffic Anomaly /                  PEAK-HOUR ANALYSIS
   Possible Incident                         |
             |                               v
             v                       AI RECOMMENDATIONS
       ALERT SERVICE

3. Implemented Components
3.1 Anomaly Detection

File:

ai-engine/src/anomaly_detector.py

The anomaly detector compares observed traffic behavior against the expected historical behavior for the same:

Road
Hour
Day of week

The following traffic signals are used:

Vehicle count
Average speed
Traffic density

The deviations from the historical baseline are combined into a weighted anomaly score.

The detector classifies traffic into:

normal
traffic_anomaly
possible_incident

A possible_incident is a proxy signal for unusual traffic behavior. It does not confirm that an actual accident has occurred.

4. Historical Baseline

File:

ai-engine/data/historical_baseline.csv

The baseline contains expected traffic behavior for road/time combinations.

Baseline dimensions:

road_id
hour
day_of_week

Expected values include:

expected_vehicle_count
expected_speed_kmph
expected_density
expected_congestion

The anomaly detector uses these values to identify deviations from normal historical behavior.

5. Anomaly Score

The anomaly score combines three traffic deviations:

Vehicle-count deviation
Speed deviation
Density deviation

The weighted score is:

Anomaly Score =
    0.40 × Vehicle Deviation
  + 0.30 × Speed Deviation
  + 0.30 × Density Deviation

Vehicle count has the highest contribution because unusual traffic volume is an important signal of abnormal road conditions.

6. Data-Driven Anomaly Thresholds

During M3 Day 5, the anomaly-score distribution was analyzed using the available historical traffic dataset.

The observed distribution was:

Percentile	Anomaly Score
P90	0.0650
P95	0.0822
P97	0.0936
P98	0.1023
P99	0.1132
Maximum	0.1564

The final thresholds were selected as:

P95 → anomaly threshold
P99 → possible-incident threshold

This provides a data-driven distinction between general unusual traffic and stronger incident-like signals.

7. Possible-Incident Logic

Possible-incident classification is intentionally conservative.

A record is classified as:

possible_incident

when:

The anomaly score reaches the P99 incident threshold.
At least two independent traffic signals are strong.
The observed congestion level differs from the expected historical congestion level.

The independent signals are:

Vehicle deviation
Speed deviation
Density deviation

This prevents a single unusual feature from automatically being treated as a possible incident.

8. Anomaly Validation Results

The historical dataset contains:

4032 observations

Final classification results:

202 anomaly records
189 traffic_anomaly
13 possible_incident

Additionally:

0 possible incidents
where expected and observed congestion levels were the same

These values describe the detector's output on the available historical dataset.

They should NOT be interpreted as a formal false-positive rate because the dataset does not contain confirmed accident ground-truth labels.

9. Anomaly API

The anomaly detector was integrated into the AI Engine through:

GET /api/v1/ai/anomalies

Optional parameter:

road_id

Example:

GET /api/v1/ai/anomalies?road_id=R001

The endpoint analyzes historical traffic observations for the requested road and returns records classified as:

traffic_anomaly
possible_incident

Normal observations are not returned in the anomaly feed.

10. Anomaly API Response

Example response:

[
  {
    "road_id": "R001",
    "time": "2026-07-28T20:00:00+05:30",
    "expected_level": "Medium",
    "observed_level": "High",
    "flagged_as": "possible_incident"
  }
]

The response contains:

road_id
time
expected_level
observed_level
flagged_as
11. Anomaly API Error Handling

For an invalid road ID:

GET /api/v1/ai/anomalies?road_id=INVALID

The API returns:

404 Not Found

Example:

{
  "detail": "No historical traffic found for road INVALID"
}

This prevents invalid road requests from silently returning misleading results.

12. AI Recommendation Engine

File:

ai-engine/src/recommendation_engine.py

The recommendation engine combines:

M2 trained congestion prediction model
Historical traffic trends
Historical baseline information
Recurring peak-hour analysis

The engine generates recommendations for a specific road.

13. M2 Model Integration

The recommendation engine uses the existing M2 trained model:

ai-engine/models/model-v1.joblib

The model is used to obtain congestion predictions for the latest available traffic observation.

The predicted congestion level and confidence are then used as part of the recommendation logic.

The recommendation engine does not replace the M2 model.

It builds additional AI insight functionality on top of the existing M2 prediction capability.

14. Historical Traffic Integration

The recommendation engine uses historical traffic data from Intern 2.

Primary dataset:

ai-engine/data/historical_traffic_4weeks_cleaned.csv

The historical data is used for:

Traffic trend analysis
Peak-hour identification
Recurring congestion detection
Road-specific recommendations
15. Recommendation API

The recommendation service is exposed through:

GET /api/v1/ai/recommendations

Required parameter:

road_id

Example:

GET /api/v1/ai/recommendations?road_id=R001
16. Recommendation API Response

Example:

[
  {
    "recommendation_text": "Avoid the recurring busy period (17:00–19:00) when possible.",
    "based_on": "Historical traffic trends for this road show consistently higher traffic during these periods."
  }
]

The response provides:

recommendation_text
based_on

The based_on field explains the historical or model basis of the recommendation.

17. Recommendation Logic

The recommendation engine considers the predicted congestion level.

For example:

High / Severe
    ↓
Suggest leaving earlier to avoid congestion

Medium
    ↓
Suggest allowing additional travel time

The engine also analyzes recurring peak periods.

If a road consistently experiences high traffic during a particular period, the recommendation can advise avoiding that period when possible.

18. Peak-Hour Analysis

During M3 Day 5, historical traffic patterns were analyzed across all six roads.

The strongest traffic activity consistently clustered around:

17:00–20:00

However, the exact peak hours varied between roads.

Examples:

R001 → 17:00–19:00
R003 → 18:00–20:00

The recommendation output was refined to combine consecutive high-traffic hours into readable time windows instead of displaying isolated hour values.

Example:

17, 18, 19

becomes:

17:00–19:00
19. Example Recommendation

For R001:

Recommendation:
Avoid the recurring busy period (17:00–19:00) when possible.

Based on:
Historical traffic trends for this road show consistently higher traffic during these periods.
20. Recommendation API Error Handling

For an invalid road:

GET /api/v1/ai/recommendations?road_id=INVALID

The API returns:

404 Not Found

Example:

{
  "detail": "No recommendation data found for road INVALID"
}
21. M2 Dependencies

The M3 AI/ML implementation depends on the following M2 components.

Trained Model
ai-engine/models/model-v1.joblib

Purpose:

Current congestion prediction
Historical Traffic Dataset
ai-engine/data/historical_traffic_4weeks_cleaned.csv

Purpose:

Historical baseline
Anomaly detection
Peak-hour analysis
Traffic trend analysis
Recommendation generation
Historical Baseline
ai-engine/data/historical_baseline.csv

Purpose:

Expected traffic behavior
Anomaly comparison
Possible-incident detection
22. Main AI/ML Project Structure
ai-engine/
│
├── app.py
│
├── src/
│   ├── __init__.py
│   ├── anomaly_detector.py
│   ├── recommendation_engine.py
│   ├── predict.py
│   ├── features.py
│   ├── train_model.py
│   └── analyze_labels.py
│
├── data/
│   ├── traffic.csv
│   ├── historical_traffic_4weeks_cleaned.csv
│   └── historical_baseline.csv
│
├── models/
│   └── model-v1.joblib
│
└── tests/
    ├── test_anomaly_detector.py
    ├── test_recommendation_engine.py
    └── test_predict.py
23. Testing

The complete AI/ML test suite was executed using:

PYTHONPATH=ai-engine/src pytest -q ai-engine/tests

Final result:

15 passed

Test breakdown:

Anomaly Detector       → 6/6 passed
Recommendation Engine  → 5/5 passed
Prediction Contract    → 4/4 passed

Total:

15/15 tests passed
24. Anomaly Detector Tests

The anomaly detector tests validate:

Threshold calculation
Threshold ordering
Normal traffic classification
Possible-incident detection
Vehicle deviation impact
Speed-drop impact
Missing-baseline handling

Final result:

6/6 passed
25. Recommendation Engine Tests

The recommendation tests validate:

Engine initialization
Recommendations for known roads
Response schema
Invalid road handling
Peak-hour detection

Final result:

5/5 passed
26. Prediction Contract Tests

The prediction tests validate the M2 model prediction contract.

They verify that the model:

Returns a valid congestion level
Returns a confidence value
Accepts the required traffic features

Final result:

4/4 passed
27. API Regression Testing

The following endpoints were validated.

AI Engine Health
GET /

Result:

200 OK

Response:

{
  "service": "TrafficVision AI Engine",
  "status": "running"
}
Anomaly API
GET /api/v1/ai/anomalies?road_id=R001

Result:

200 OK
Recommendation API
GET /api/v1/ai/recommendations?road_id=R001

Result:

200 OK
Invalid Anomaly Road
GET /api/v1/ai/anomalies?road_id=INVALID

Result:

404 Not Found
Invalid Recommendation Road
GET /api/v1/ai/recommendations?road_id=INVALID

Result:

404 Not Found
28. Performance Validation

Local response-time measurements were performed for both AI endpoints.

Approximate results:

Endpoint	Average Local Response Time
Anomaly Detection	~0.20 seconds
AI Recommendations	~0.05 seconds

The current local measurements did not indicate a need for additional optimization.

These measurements are local development measurements and should not be interpreted as production performance benchmarks.

29. AI Insights Summary

The M3 AI Insights functionality can be summarized as:

ANOMALY DETECTION

Historical traffic
        ↓
Road/time baseline
        ↓
Vehicle + Speed + Density deviations
        ↓
Weighted anomaly score
        ↓
Normal / Traffic Anomaly / Possible Incident

and:

TRAFFIC RECOMMENDATIONS

M2 congestion model
        +
Historical traffic trends
        +
Peak-hour analysis
        ↓
Road-specific recommendation
30. AI Insights Limitations
Possible Incident

The system detects unusual traffic patterns that may indicate an incident.

It does NOT confirm that an accident has occurred.

The output should therefore be interpreted as:

possible_incident

rather than:

confirmed_accident

Additional evidence would be required for confirmation.

31. False-Positive Limitation

A formal false-positive rate cannot currently be calculated.

Reason:

The available historical traffic dataset does not contain
confirmed accident ground-truth labels.

Therefore:

13 possible incidents / 4032 observations

should only be described as the current detection rate on the historical dataset.

It should NOT be reported as a false-positive rate.

32. Recommendation Limitations

Recommendations are based on:

Historical traffic behavior
M2 congestion predictions
Recurring peak-hour patterns

Unexpected real-time events may not be represented by the historical patterns.

Therefore, recommendations should be treated as decision-support information rather than guaranteed travel outcomes.

33. Cross-Team Dependency — Intern 1

The anomaly service is designed to provide possible-incident signals to the Alert Service.

Expected Alert Service endpoint:

POST /api/v1/alerts/

Expected request:

{
  "type": "accident",
  "severity": "High",
  "road_id": "R001",
  "message": "Anomalous traffic pattern detected on road R001, flagged as possible_incident."
}

Expected successful response:

201 Created

Example:

{
  "alert_id": "alt_984123",
  "status": "created",
  "road_id": "R001"
}

At the time of handoff, final end-to-end Alert Service connectivity and validation remain a cross-team dependency with Intern 1.

The AI/ML anomaly detector itself has been tested independently.

34. Cross-Team Dependency — Intern 5

Final QA validation remains a dependency.

Expected QA activities include:

Defect-log validation
Cross-module regression
End-to-end validation
Final M3 QA sign-off

AI/ML unit and API regression testing has already been completed independently.

35. M3 Day-Wise Implementation Summary
Day 1 — Planning and Data Contract

Reviewed:

M2 trained congestion model
Historical traffic data
M3 requirements

Finalized AI/ML scope:

Anomaly / possible-incident detection
+
AI traffic recommendations

Confirmed required data and implementation approach.

Day 2 — Anomaly Prototype

Developed the historical-baseline anomaly detector.

Compared:

Observed traffic
vs
Expected historical traffic

using:

Vehicle count
Average speed
Traffic density

Developed the initial anomaly scoring and classification logic.

Day 3 — Anomaly API

Integrated the detector into the AI Engine.

Implemented:

GET /api/v1/ai/anomalies

Added:

Road filtering
Anomaly classification
Possible-incident classification
Error handling
Day 4 — AI Recommendations

Implemented:

recommendation_engine.py

Integrated:

M2 congestion model
+
Historical traffic trends
+
Peak-hour analysis

Implemented:

GET /api/v1/ai/recommendations
Day 5 — Tuning and Refinement

Performed anomaly sensitivity analysis.

Finalized:

P95 → anomaly threshold
P99 → possible-incident threshold

Refined possible-incident logic to require multiple strong signals and a congestion-level mismatch.

Analyzed recurring peak-hour patterns across all six roads.

Improved recommendation output by converting consecutive peak hours into readable time windows.

Day 6 — Testing and Performance

Completed:

Unit testing
API regression testing
Invalid-input testing
Latency validation

Final result:

15/15 tests passed

Approximate local response times:

Anomaly API          → ~0.20 sec
Recommendation API   → ~0.05 sec
Day 7 — Final Validation and Handoff

Completed:

AI/ML regression testing
API health validation
Valid road validation
Invalid road validation
AI Insights preparation
M4 handoff documentation

Final test result:

15/15 passed

Remaining external dependencies:

Intern 1 → Alert Service integration validation
Intern 5 → Final QA / defect-log validation
36. M4 Handoff Checklist
AI/ML
 Anomaly detector implemented
 Historical baseline generated
 Data-driven thresholds validated
 Possible-incident logic implemented
 Recommendation engine implemented
 M2 model integrated
 Historical trend analysis integrated
 Peak-hour analysis implemented
 Anomaly API implemented
 Recommendation API implemented
 Unit tests completed
 API regression completed
 Performance validation completed
 AI Insights content prepared
Cross-Team
 Final Alert Service integration with Intern 1
 End-to-end alert validation
 Intern 5 QA defect-log validation
 Final cross-team sign-off
37. Important Files for Future Maintenance
ai-engine/app.py

Contains the AI Engine API endpoints.

ai-engine/src/anomaly_detector.py

Contains anomaly detection and possible-incident logic.

ai-engine/src/recommendation_engine.py

Contains AI recommendation logic.

ai-engine/src/predict.py

Contains M2 congestion prediction functionality.

ai-engine/models/model-v1.joblib

Contains the trained M2 congestion model.

ai-engine/data/historical_traffic_4weeks_cleaned.csv

Historical traffic dataset.

ai-engine/data/historical_baseline.csv

Historical expected traffic baseline.

ai-engine/tests/test_anomaly_detector.py

Anomaly detection tests.

ai-engine/tests/test_recommendation_engine.py

Recommendation engine tests.

ai-engine/tests/test_predict.py

Prediction contract tests.

38. Recommended Validation After Future Changes

Whenever AI/ML code or the underlying data/model is changed, run:

PYTHONPATH=ai-engine/src pytest -q ai-engine/tests

Then validate:

curl -s "http://127.0.0.1:8010/"

Anomaly API:

curl -i "http://127.0.0.1:8010/api/v1/ai/anomalies?road_id=R001"

Recommendation API:

curl -i "http://127.0.0.1:8010/api/v1/ai/recommendations?road_id=R001"

Invalid anomaly request:

curl -i "http://127.0.0.1:8010/api/v1/ai/anomalies?road_id=INVALID"

Invalid recommendation request:

curl -i "http://127.0.0.1:8010/api/v1/ai/recommendations?road_id=INVALID"

Expected:

Health                         → 200
Anomaly API                    → 200
Recommendation API             → 200
Invalid anomaly road           → 404
Invalid recommendation road    → 404
Test suite                     → 15 passed
39. M3 Final Status

The M3 AI/ML implementation is functionally complete and locally validated.

Completed:

Anomaly Detection
Possible-Incident Detection
AI Recommendations
M2 Model Integration
Historical Trend Integration
Peak-Hour Analysis
AI APIs
Unit Testing
API Regression
Performance Validation
AI Insights Preparation
M4 Handoff Documentation

Remaining work is primarily cross-team:

Alert Service integration and validation — Intern 1
Final QA / defect-log validation — Intern 5
40. Final Handoff Summary

TrafficVision AI's M3 AI/ML layer extends the M2 congestion prediction system with two major capabilities:

1. Detect unusual traffic behavior and flag possible incidents.

2. Generate road-specific traffic recommendations
   using model predictions and historical traffic patterns.

The implementation has been tested locally with:

15/15 AI/ML tests passing

and both AI endpoints have been validated for valid and invalid road IDs.

The main limitation is that possible-incident detection is a proxy for unusual traffic behavior and does not confirm an actual accident. A formal false-positive rate cannot be calculated without confirmed accident ground-truth data.

The next integration step is to connect the AI anomaly output with the Alert Service and complete final QA validation before full M3 sign-off.
```
