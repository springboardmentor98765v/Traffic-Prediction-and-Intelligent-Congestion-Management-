---

## Intern 3 — Day 1 ML & Routing Plan

### ML Pipeline

Historical Traffic Data
↓
Data Validation
↓
Data Cleaning
↓
Temporal Feature Extraction
↓
Feature Engineering
↓
Train / Validation / Test Split
↓
Baseline Classification Models
↓
Model Evaluation
↓
Model Selection
↓
model-v1
↓
Prediction Service

### Prediction Outputs

The ML module will support:

1. Congestion prediction
2. Peak-hour forecasting
3. Delay estimation

### Congestion Prediction

Input:

- road_id
- timestamp
- vehicle_count
- avg_speed_kmph
- traffic_density
- road_capacity
- road_length_km
- temporal features
- historical traffic features

Output:

- road_id
- predicted_level
- confidence
- generated_by

### Peak-Hour Forecasting

Historical traffic observations will be grouped by road segment
and time period to identify recurring high-congestion windows.

### Delay Estimation

The prediction service will provide an estimated delay value
associated with predicted traffic conditions.

The exact delay calculation will be finalized after the
historical dataset and available route/travel-time information
are validated.

### Intelligent Routing

The ML prediction service will provide predicted congestion
and delay information to the Route Analysis Service.

Candidate routes will be ranked using predicted traffic
conditions rather than distance alone.

Initial concept:

Route Score =
congestion component + delay component + distance component

The numerical weights will be finalized after integration
with the Route Analysis Service.

### Model Evaluation

Classification metrics:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

The trained model will be compared against the Milestone 1
heuristic baseline.

### Model Versioning

Milestone 1:

`heuristic-v0`

Milestone 2 first trained model:

`model-v1`
