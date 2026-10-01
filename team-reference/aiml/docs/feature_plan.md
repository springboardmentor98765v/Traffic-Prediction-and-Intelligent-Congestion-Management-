# Congestion Prediction Feature Plan

## Objective

Predict road congestion as `LOW`, `MEDIUM`, or `HIGH` from the traffic monitoring feed. Milestone 1 uses a transparent heuristic; Milestone 2 will replace it with a trained model after enough labeled observations are collected.

## Input contract

- `road_id`: categorical road identifier.
- `timestamp`: observation time in ISO-8601 format.
- `vehicle_count`: non-negative vehicle count for the observation interval.
- `average_speed`: non-negative average speed in km/h.
- `road_capacity`: configured capacity for the road, defaulting to 200 vehicles per interval until road metadata is available.

## Candidate features

1. `density = vehicle_count / road_capacity`: primary congestion signal.
2. `average_speed`: inverse congestion signal and a useful fallback when capacity is unknown.
3. `hour`: extracted from `timestamp`.
4. `is_peak_hour`: morning peak 08:00-10:59 or evening peak 17:00-19:59.
5. `day_of_week`: useful for weekday/weekend demand differences.
6. `road_id`: categorical identity; encode with one-hot encoding or a learned embedding, never as an ordinal number.
7. Rolling features for Milestone 2: 15/30/60-minute mean speed, count trend, and lagged congestion label.

## Milestone 1 heuristic

- `HIGH` when density is at least 1.0 or average speed is below 20 km/h.
- `MEDIUM` when density is at least 0.6 or average speed is below 35 km/h.
- Otherwise `LOW`.
- Promote `LOW` to `MEDIUM` during peak hours.

The thresholds are provisional and must be recalibrated against observed labels. The model version is `heuristic-v0` so consumers can distinguish it from a trained model.

## Milestone 2 modeling approach

1. Build labels from sustained low-speed/high-density windows and validate them with domain review.
2. Split chronologically by time to avoid future leakage; keep roads represented in each split where possible.
3. Establish a majority-class baseline, then compare logistic regression, random forest, and gradient-boosted trees.
4. Use a preprocessing pipeline for numeric imputation/scaling and categorical encoding.
5. Evaluate macro F1, per-class recall, confusion matrix, and calibration. High-congestion recall is the safety-critical metric.
6. Save the complete preprocessing and model pipeline, version it, and expose the same response contract.
7. Monitor missingness, feature drift, class balance, and prediction distribution after deployment.

## Open data dependencies

- Intern 2 live feed URL and exact schema.
- Per-road capacity and speed-limit metadata.
- Confirmed congestion label definition and acceptable prediction horizon.
