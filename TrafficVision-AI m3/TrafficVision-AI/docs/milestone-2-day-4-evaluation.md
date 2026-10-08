# Milestone 2 — Day 4 Model Evaluation Report

## 1. Objective

Evaluate the trained traffic congestion prediction model using
chronological train/test validation, analyze classification performance,
identify limitations, and document the peak-hour and delay estimation logic.

---

## 2. Model Used

The final model is a Random Forest classifier trained using traffic
observations from `traffic.csv`.

### Model Configuration

- Algorithm: Random Forest Classifier
- Number of trees: 300
- Class weighting: Balanced
- Random state: 42
- Parallel training: Enabled
- Validation strategy: Chronological 80/20 split

The model artifact is saved as:

`ai-engine/models/model-v1.joblib`

---

## 3. Feature Set

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

Temporal features are derived from the traffic timestamp.

---

## 4. Chronological Validation

To avoid random mixing of past and future observations, the dataset was
sorted chronologically before splitting.

### Training Set

- Samples: 1156
- Period: 2026-08-25 06:00:00 → 2026-08-26 14:00:00

### Testing Set

- Samples: 290
- Period: 2026-08-26 14:00:00 → 2026-08-26 22:00:00

This provides a more realistic validation setup for time-dependent
traffic data than a purely random split.

---

## 5. Evaluation Results

| Metric             | Result |
| ------------------ | -----: |
| Accuracy           | 98.62% |
| Weighted Precision | 98.43% |
| Weighted Recall    | 98.62% |
| Weighted F1-score  | 98.46% |

---

## 6. Classification Report

| Class  | Precision | Recall | F1-score | Support |
| ------ | --------: | -----: | -------: | ------: |
| Low    |      1.00 |   1.00 |     1.00 |      95 |
| Medium |      1.00 |   1.00 |     1.00 |     140 |
| High   |      0.94 |   0.98 |     0.96 |      50 |
| Severe |      0.67 |   0.40 |     0.50 |       5 |

### Macro Average

- Precision: 0.90
- Recall: 0.84
- F1-score: 0.87

### Weighted Average

- Precision: 0.98
- Recall: 0.99
- F1-score: 0.98

---

## 7. Confusion Matrix

The chronological test-set confusion matrix was:

````text
                Predicted
              Low Medium High Severe

Actual Low      95    0     0     0
Actual Medium    0  140     0     0
Actual High      0    0    49     1
Actual Severe    0    0     3     2

---

## 8. MAE and RMSE — Ordinal Error Analysis

Although the congestion model is a multiclass classification model, the
congestion labels have an inherent ordinal relationship:

```text
Low = 0
Medium = 1
High = 2
Severe = 3
````
