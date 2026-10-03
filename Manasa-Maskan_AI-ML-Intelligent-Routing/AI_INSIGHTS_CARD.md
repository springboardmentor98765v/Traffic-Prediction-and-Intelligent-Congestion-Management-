# TrafficVision AI - Milestone 3 AI Insights Card

## 1. Module

AI Insights Module

Owner: Manasa Maskan
Domain: AI/ML and Intelligent Routing
Milestone: Milestone 3

---

## 2. Purpose

The AI Insights module uses historical traffic data and the
Milestone 2 traffic prediction model to identify unusual traffic
patterns and generate explainable traffic recommendations.

The anomaly detection system identifies unusual traffic behavior
as possible incidents.

An anomaly is NOT treated as a confirmed accident.

---

## 3. AI Components

The AI Insights module contains:

1. Traffic prediction
2. Traffic condition classification
3. Anomaly detection
4. Anomaly threshold tuning
5. Traffic recommendations
6. API endpoints
7. Unit and integration-style tests

---

## 4. Traffic Prediction Model

The Milestone 2 Random Forest model predicts vehicle count using:

- Road/Junction ID
- Hour
- Day of week
- Month

The prediction is then converted into a traffic condition:

- Low Traffic
- Medium Traffic
- High Traffic

---

## 5. Anomaly Detection

The anomaly detector compares:

- Expected vehicle count from the M2 model
- Observed historical vehicle count

A large difference between expected and observed traffic
is treated as a possible anomaly.

The system returns:

- Road ID
- Time
- Expected vehicles
- Observed vehicles
- Expected traffic level
- Observed traffic level
- Residual
- Anomaly score
- Possible incident flag

---

## 6. Anomaly Threshold Tuning

Different sensitivity levels were tested.

| Threshold Multiplier | Detected Anomalies |
|----------------------|-------------------:|
| 2.0 | 1473 |
| 2.5 | 855 |
| 3.0 | 479 |
| 3.5 | 260 |
| 4.0 | 152 |

Increasing the threshold reduces the number of flagged anomalies.

The threshold of 3.0 was used during the current validation
tests.

The resulting calculated residual threshold was 31.2.

---

## 7. Current Validation Result

For threshold multiplier 3.0:

- Calculated anomaly threshold: 31.2
- Total anomalies detected: 479
- Maximum API results can be limited using max_results
- Anomaly records were successfully returned through the API

Example classification:

```text
flagged_as = possible_incident