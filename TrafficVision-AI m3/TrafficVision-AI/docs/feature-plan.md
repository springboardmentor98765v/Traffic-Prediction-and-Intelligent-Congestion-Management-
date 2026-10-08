# TrafficVision AI — Milestone 2 Feature Plan

## Objective

Define and finalize the features required for the Milestone 2
machine-learning congestion prediction model.

The Milestone 2 model will replace the Milestone 1 heuristic
congestion predictor.

---

## Existing Traffic Data

The historical traffic dataset contains traffic observations
for individual road segments over time.

Relevant fields include:

- road_id
- road_name
- sensor_id
- timestamp
- vehicle_count
- avg_speed_kmph
- road_capacity
- congestion_level
- latitude
- longitude
- road_length_km
- traffic_density

---

## Finalized ML Features

| Feature               | Type        | Description                             | Expected Use                |
| --------------------- | ----------- | --------------------------------------- | --------------------------- |
| vehicle_count         | Numeric     | Number of vehicles observed             | Traffic volume              |
| avg_speed_kmph        | Numeric     | Average vehicle speed                   | Traffic-flow indicator      |
| traffic_density       | Numeric     | Vehicle count relative to road capacity | Congestion indicator        |
| road_capacity         | Numeric     | Maximum/reference road capacity         | Traffic utilization         |
| road_length_km        | Numeric     | Length of road segment                  | Road characteristics        |
| hour                  | Numeric     | Hour extracted from timestamp           | Peak-hour patterns          |
| day_of_week           | Numeric     | Day extracted from timestamp            | Weekly traffic patterns     |
| road_id               | Categorical | Road segment identifier                 | Road-specific patterns      |
| historical_congestion | Categorical | Previous/available congestion state     | Historical traffic behavior |

---

## Derived Temporal Features

The following features will be generated from `timestamp`:

- hour
- day_of_week
- is_weekend

These features will help the model learn recurring traffic patterns.

---

## Derived Historical Features

Where sufficient historical observations are available, the
following features may be generated:

- previous congestion level
- rolling average congestion
- rolling average vehicle count

These features will capture recent traffic behavior.

---

## Density Feature

Traffic density/utilization is calculated as:

traffic_density = vehicle_count / road_capacity

The dataset already contains `traffic_density`, so the existing
value will be validated against this relationship before model
training.

---

## Target

Primary prediction target:

`congestion_level`

The target labels will use the congestion categories already
present in the historical dataset.

---

## Feature Selection Decision

### Primary features

- vehicle_count
- avg_speed_kmph
- traffic_density
- road_capacity
- road_length_km
- hour
- day_of_week
- road_id

### Historical features

- historical_congestion
- previous congestion where available
- rolling traffic statistics where sufficient history exists

---

## Milestone 1

Milestone 1 used EDA and a rule-based heuristic predictor.

Current heuristic:

- Density < 10 → Low
- Density 10–19.99 → Medium
- Density >= 20 → High

Model version:

`heuristic-v0`

---

## Milestone 2

Milestone 2 will evaluate trained machine-learning
classification models against the Milestone 1 heuristic.

Initial candidate models:

- Logistic Regression
- Random Forest
- Gradient Boosting

The best-performing reliable model will be selected as `model-v1`.
