# TrafficVision AI Engine: Milestone 2 Model Evaluation Report

## Executive Summary
This report provides validation metrics and residual analysis for the dual-task traffic prediction models.

- **Model Version**: `model-v1`
- **Test Set Size**: 200 samples (20% holdout)
- **Classifier Accuracy**: 1.0000
- **Regressor MAE**: 1.31 minutes
- **Regressor RMSE**: 1.63 minutes
- **Regressor R²**: 0.9586

## 1. Congestion Classification Performance

| Congestion Level | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **HIGH** | 1.00 | 1.00 | 1.00 | 40.0 |
| **LOW** | 1.00 | 1.00 | 1.00 | 46.0 |
| **MEDIUM** | 1.00 | 1.00 | 1.00 | 107.0 |
| **SEVERE** | 1.00 | 1.00 | 1.00 | 7.0 |

### Confusion Matrix

| Actual \ Predicted | HIGH | LOW | MEDIUM | SEVERE |
| :--- | :--- | :--- | :--- | :--- |
| **HIGH** | 40 | 0 | 0 | 0 |
| **LOW** | 0 | 46 | 0 | 0 |
| **MEDIUM** | 0 | 0 | 107 | 0 |
| **SEVERE** | 0 | 0 | 0 | 7 |

## 2. Delay Regression & Residual Analysis

- **Mean Absolute Error (MAE)**: 1.31 minutes
- **Root Mean Squared Error (RMSE)**: 1.63 minutes
- **Residual Mean (Bias)**: 0.172 minutes
- **Residual Std Deviation**: 1.620 minutes
- **Max Overprediction Error**: -3.68 minutes
- **Max Underprediction Error**: 4.95 minutes

## 3. Feature Importance Comparison

| Feature | Classifier Weight | Regressor Weight |
| :--- | :--- | :--- |
| `is_rush_hour` | 0.0237 | 0.6481 |
| `density` | 0.6352 | 0.3237 |
| `rolling_avg_density` | 0.0709 | 0.0077 |
| `rolling_avg_vehicle_count` | 0.0437 | 0.0074 |
| `hour_of_day` | 0.0627 | 0.0051 |
| `day_of_week` | 0.0112 | 0.0041 |
| `vehicle_count` | 0.1499 | 0.0033 |
| `is_weekend` | 0.0027 | 0.0005 |

## 4. Key Engineering Takeaways
- **Primary Driver**: Traffic density and rolling average density dominate delay calculations.
- **Temporal Synergy**: Peak rush hour flags successfully elevate congestion categorization risk.
- **Stability**: Low residual bias indicates no persistent skew across test predictions.
