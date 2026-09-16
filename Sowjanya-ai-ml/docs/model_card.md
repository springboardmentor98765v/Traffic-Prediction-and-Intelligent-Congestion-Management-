# TrafficVision AI – Model Card

## Model
Decision Tree Classifier

## Model Version
model-v1

## Purpose
Predict traffic congestion levels using traffic-related features.

## Input Features
- road_id_encoded
- vehicle_count
- avg_speed
- density
- hour
- day_of_week
- is_peak_hour

## Target
Congestion level:
- Low
- Medium
- High

## Training Data
processed_traffic.csv

Dataset size:
840 rows

## Evaluation
Test Accuracy: 1.00

5-Fold Cross-Validation:
Mean Accuracy: 99.88%

## Important Observation
Density was the dominant feature in the current dataset,
with feature importance of 1.0.

This indicates that the current congestion labels are
strongly associated with traffic density.

The evaluation results should not be interpreted as
guaranteed real-world accuracy.

## Latency
Average prediction latency:
4.13 ms per prediction

Tested over:
100 predictions

## Route Ranking
Routes are ranked using:
- distance
- estimated delay
- predicted congestion penalty

Lower congestion score receives a higher route rank.

## API Integration
The model is integrated with the Traffic Prediction Service.

Model version:
model-v1

## Limitations
- Current training dataset is limited.
- Density dominates the current prediction.
- Real-world performance requires more diverse traffic data.
- Peak-hour and delay components are currently implemented
  as service logic rather than separately trained forecasting
  and regression models.

## M3 Handoff
The model and prediction service are ready for continued
integration and future improvement with larger traffic data.