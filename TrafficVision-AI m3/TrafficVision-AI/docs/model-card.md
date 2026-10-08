# TrafficVision AI — Model Card

## 1. Model Overview

**Model Name:** TrafficVision AI Congestion Classifier  
**Model Version:** model-v1  
**Model Type:** Random Forest Classifier  
**Task:** Traffic congestion-level classification  
**Framework:** scikit-learn

The model predicts the congestion level of a road using traffic,
road, and time-based features.

---

## 2. Intended Use

The model is intended to support the TrafficVision AI platform by providing
congestion predictions that can be consumed by the Prediction Service and
used as an input to intelligent route ranking.

The model predicts the following congestion classes:

- Low
- Medium
- High
- Severe

---

## 3. Input Features

The final model uses the following features:

- `vehicle_count`
- `avg_speed_kmph`
- `road_capacity`
- `road_length_km`
- `traffic_density_vehicles_per_km`
- `hour`
- `day_of_week`
- `is_weekend`
- `road_id`

The timestamp is transformed into time-based features during preprocessing.

---

## 4. Training Data

The model was trained using the available TrafficVision AI traffic dataset.

Dataset shape:

- **Rows:** 1,446
- **Columns:** 12

Congestion label distribution:

| Class  | Samples |
| ------ | ------: |
| Low    |     747 |
| Medium |     496 |
| High   |     184 |
| Severe |      19 |

The dataset contains no missing values and no duplicate records.

---

## 5. Training & Validation Strategy

A chronological/time-based train-test split was used to reduce
random mixing of earlier and later traffic observations.

| Dataset  | Samples |
| -------- | ------: |
| Training |   1,156 |
| Testing  |     290 |

Training period:

```text
2026-08-25 06:00:00 → 2026-08-26 14:00:00
```
