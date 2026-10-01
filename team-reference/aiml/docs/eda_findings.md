# EDA Findings Summary

Dataset: `data/processed/processed_traffic.csv`

- 15 rows, 6 columns, 3 roads (`R001`-`R003`).
- The processed schema contains `road_id`, `timestamp`, `vehicle_count`, `average_speed`, `congestion_level`, and `hour`.
- No missing values were observed in the provisional dataset.
- Observations cover 08:00-09:00, so the dataset does not yet support full-day or weekday/weekend analysis.
- Vehicle count increases as average speed decreases in the sample. This supports density/count and speed as candidate predictors.
- `congestion_level` is strongly derived from average speed in the current processing script, so it must not be treated as an independent training label without a new labeling rule.
- `road_id` should be retained as a categorical feature. It may capture road-specific capacity, but it must not be encoded as an arbitrary numeric rank.
- `hour` is currently present and should be expanded to peak/off-peak and, once data is available, cyclic time features.

## Recommended next data collection

Collect several weeks of observations across all hours, weekdays, road capacities, incidents, and weather conditions. Add a stable observation interval and a reviewed target label before training a model.
