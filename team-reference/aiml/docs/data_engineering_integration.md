# Data Engineering Integration

The AI/ML service consumes the Data Engineering export through the existing feature builder and serves the retrained `ml-v2` artifact.

## Configuration

Set `TRAFFIC_DATA_API_URL` to the Data Engineering service's versioned API base, for example:

```powershell
$env:TRAFFIC_DATA_API_URL = "http://127.0.0.1:8000/api/v1"
```

The default local source is `data/external/traffic_readings_export.csv`. The old prototype CSV files are not used by the training command or default API path.

## Data flow

```text
Data Engineering traffic API
  -> src.data_engineering_adapter.TrafficDataAdapter
  -> canonical traffic DataFrame
  -> src.prediction_model.build_features
  -> models/congestion_model.joblib (ml-v2)
  -> FastAPI prediction, delay, and route endpoints
```

## Field mapping

| Data Engineering field | AI/ML field | Handling |
|---|---|---|
| `road_id` | `road_id` | Converted to string; no invented numeric-to-Rxxx mapping |
| `recorded_at` | `timestamp` | Parsed as a pandas datetime |
| `vehicle_count` | `vehicle_count` | Numeric value preserved |
| `avg_speed_kmph` | `average_speed` | Renamed and converted to numeric |
| `density` | source density | Retained and used by `ml-v2` |
| `congestion_level` | `congestion_level` | `MODERATE` is normalized to `MEDIUM`; `SEVERE` remains separate |

The Data Engineering repository's feed is synthetic/demo data generated into PostgreSQL. It is not a real sensor stream.

## Consumed endpoints

- `GET /traffic/live`
- `GET /traffic/history?limit=10000`
- `GET /traffic/road/{road_id}`

The AI service now uses `data/external/traffic_readings_export.csv` as its default and only training source. The retrained artifact is `ml-v2`. The old prototype CSV files are no longer used by the training script or default FastAPI data path.
