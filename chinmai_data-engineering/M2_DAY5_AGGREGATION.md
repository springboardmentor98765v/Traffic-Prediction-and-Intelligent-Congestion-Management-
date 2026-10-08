# M2 Day 5 - Traffic Aggregation and Query Optimization

## Objective

Produce summarized hourly and daily traffic metrics per road to
support Intern 3's feature engineering.

The implementation also optimizes road/time lookups using PostgreSQL
indexes and verifies query performance using EXPLAIN ANALYZE.

## Existing Data Source

The aggregation is generated from:

`traffic_history`

## Hourly Metrics

The `hourly_traffic_metrics` table contains:

- road_id
- metric_timestamp
- avg_vehicle_count
- max_vehicle_count
- avg_speed_kmph
- min_speed_kmph
- avg_density
- max_density
- total_readings
- high_congestion_count
- severe_congestion_count
- high_congestion_percentage
- severe_congestion_percentage

## Daily Metrics

The `daily_traffic_metrics` table contains:

- road_id
- metric_date
- avg_vehicle_count
- max_vehicle_count
- avg_speed_kmph
- min_speed_kmph
- avg_density
- max_density
- total_readings
- high_congestion_count
- severe_congestion_count
- high_congestion_percentage
- severe_congestion_percentage

## Aggregation Script

Run:

```powershell
python .\src\generate_traffic_aggregates.py