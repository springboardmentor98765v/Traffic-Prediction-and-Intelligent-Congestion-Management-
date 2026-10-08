# Milestone 3 — AI/ML Plan

## Intern 3 — AI/ML & Intelligent Routing

### 1. Objective

Milestone 3 extends the Milestone 2 traffic prediction system with:

1. Traffic anomaly detection
2. Possible incident/accident-pattern detection
3. AI-based traffic recommendations

The M3 AI components will reuse the trained Milestone 2 congestion model
(`model-v1`) and incorporate historical/trend information provided by
Intern 2.

---

## 2. Milestone 2 AI Foundation

Milestone 2 completed:

- Traffic feature engineering
- Congestion classification
- Chronological train/test validation
- Model evaluation
- Trained model saved as `model-v1.joblib`
- Congestion prediction
- Peak-hour prediction
- Delay estimation
- Congestion-aware route ranking

### M2 Model

Model version:

`model-v1`

Model artifact:

`ai-engine/models/model-v1.joblib`

Primary target:

`congestion_level`

Expected classes:

- Low
- Medium
- High
- Severe

---

## 3. M3 Architecture

```text
                 Traffic Data
                      |
                      v
              M2 model-v1
                      |
          Predicted traffic state
                      |
          +-----------+-----------+
          |                       |
          v                       v
   Anomaly Detection       Recommendation Engine
          |                       |
          |                 M2 predictions
          |                       +
          |                 Historical trends
          v                       |
   Possible incident              v
          |                 AI recommendation
          v
   Alert integration
```
