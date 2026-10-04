# TrafficVision AI — Milestone 3 AI Insights Card

## 1. AI Module Overview

The AI module extends the Milestone 2 traffic prediction model with:

- Traffic anomaly detection
- Possible incident detection
- AI-based traffic recommendations
- Alert Service integration

## 2. Anomaly Detection

The system compares predicted traffic with observed traffic.

Large deviations between expected and observed traffic are flagged as:

possible_incident

Anomaly detection is used as a proxy for possible accidents/incidents.

## 3. Alert Integration

When a possible incident is detected, the AI service automatically sends an alert to:

POST /api/v1/alerts

The alert contains:

- type: possible_incident
- severity: high
- road_id
- message

The Alert Service returns a generated alert ID.

## 4. AI Recommendations

The recommendations API is:

GET /api/v1/ai/recommendations?road_id={id}

It provides simple traffic recommendations based on predicted traffic conditions and available traffic information.

## 5. Testing

The AI module tests were executed using pytest.

Result:

21 tests passed.

The anomaly detection and recommendation tests passed successfully.

## 6. Alert Integration Test

The anomaly API was tested with the Alert Service.

Flow:

Traffic Data
    ↓
Anomaly Detection
    ↓
Possible Incident
    ↓
POST /api/v1/alerts
    ↓
Alert Service
    ↓
Alert ID Generated

The end-to-end AI → Alert Service request was successfully tested.

## 7. Limitations

The current traffic dataset does not contain confirmed accident labels.

Therefore, a validated numerical accident false-positive rate cannot be calculated from the available dataset.

The anomaly detector should therefore be treated as a possible-incident detector rather than a confirmed accident detector.

## 8. Future Improvements

- Use labelled accident/incident data.
- Improve anomaly threshold tuning.
- Reduce repeated alerts for the same road and time period.
- Improve recommendation quality using additional historical traffic information.
- Evaluate the model using real incident outcomes.

## 9. Milestone 4 Handoff

The AI module is ready for further integration and improvement in Milestone 4.

The main areas for future improvement are anomaly validation, alert-noise reduction, additional traffic features, and evaluation using labelled incident data.