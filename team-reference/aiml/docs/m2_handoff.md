# Milestone 2 Handoff

Implemented model-backed prediction and route ranking for the AI Engine using the Data Engineering historical export.

## Endpoints

- `GET /predict/congestion?road_id=R001`
- `GET /predict/peak-hours?road_id=R001`
- `GET /predict/delay?road_id=R001&distance_km=2`
- `POST /route/rank` with `{\"routes\":[{\"route_id\":\"route-a\",\"distance_km\":2,\"roads\":[\"R001\",\"R002\"]}]}`

The `ml-v2` artifact is generated from `data/external/traffic_readings_export.csv` by `scripts/train_model.py`. The service loads it once at startup and preserves the frontend congestion response fields.

The model card records the chronological evaluation and known limitations. The source export contains synthetic Data Engineering data; confidence is not calibrated production confidence and delay remains rule-based.
