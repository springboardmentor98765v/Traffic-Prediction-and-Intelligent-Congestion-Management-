# TrafficVision AI - Milestone 3 Handoff Notes

## AI Insights Module

**Owner:** Intern 3 - AI/ML  
**Project:** TrafficVision AI - Smart Traffic Prediction & Congestion Management System  
**Milestone:** Milestone 3  
**Module:** AI Anomaly Detection and AI Recommendations

---

# 1. Module Overview

The Milestone 3 AI Insights module extends the Milestone 2 traffic prediction system.

The module provides two main AI capabilities:

1. Anomaly Detection
2. AI-based Traffic Recommendations

The anomaly detection component identifies unusual traffic patterns and treats them as possible incidents.

The recommendation component generates simple and explainable traffic recommendations using traffic predictions and historical traffic trends.

The Milestone 3 SRS defines the following AI endpoints:

- `GET /api/v1/ai/anomalies`
- `GET /api/v1/ai/recommendations?road_id={id}`

The anomaly endpoint is intended to provide:

- `road_id`
- `time`
- `expected_level`
- `observed_level`
- `flagged_as`

The recommendation endpoint is intended to provide:

- `recommendation_text`
- `based_on`

---

# 2. Files Implemented

The following AI/ML files were implemented or updated:

```text
src/
│
├── ai_engine/
│   ├── anomaly_detector.py
│   ├── recommendation_engine.py
│   ├── predictor.py
│   └── api.py
│
├── tune_anomaly.py
├── recommendation_test.py
├── test_m2_features.py
└── test_m3_features.py