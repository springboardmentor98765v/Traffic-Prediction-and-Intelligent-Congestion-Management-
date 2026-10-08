# M2 Day 3 – Historical Data API & Data Cleaning

## Objective
Expose historical traffic data to Intern 3 through APIs and deliver a validated, cleaned dataset.

## APIs

### GET `/api/v1/traffic/history`
Returns records from `traffic_history`.

Optional query parameters:
- `road_id`
- `start_time`
- `end_time`
- `limit` (1–5000, default 500)

Example:
`GET http://127.0.0.1:8000/api/v1/traffic/history?road_id=R001&limit=10`

### GET `/api/v1/traffic/aggregate`
Returns historical aggregates grouped by hour or day.

Optional query parameters:
- `road_id`
- `start_time`
- `end_time`
- `interval=hour|day` (default `day`)

Example:
`GET http://127.0.0.1:8000/api/v1/traffic/aggregate?road_id=R001&interval=day`

## Cleaning and validation

Run:
```powershell
python src/historical_data_cleaner.py
```

The cleaner:
- removes duplicate `(road_id, sensor_id, timestamp)` records;
- removes invalid metric rows;
- detects hourly gaps per road;
- sorts the cleaned data chronologically;
- writes `data/historical_traffic_4weeks_cleaned.csv`;
- writes `docs/M2_DAY3_DATA_QUALITY_REPORT.md`.

For the current M2 Day 2 dataset, the expected clean result is 4,032 records, 6 roads, 672 records per road, and no hourly gaps.

## Intern 3 handoff

Intern 3 can retrieve historical records directly from the history API and use the aggregate API for daily/hourly feature preparation.
