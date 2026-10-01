# Milestone 1 Handoff

## Scope signed off

The AI Engine currently provides a transparent heuristic prediction service. It is not a trained ML model. The current model identifier is `heuristic-v0`.

## API contract

`GET /predict/congestion`

Required query parameter: `road_id`.

Optional live-observation query parameters: `vehicle_count`, `average_speed`, and ISO-8601 `timestamp`. When all three are supplied, the service predicts directly from that observation. When they are omitted, the service uses the latest matching record from the local processed CSV as a development fallback.

Response fields:

- `road_id`
- `predicted_level`: `LOW`, `MEDIUM`, or `HIGH`
- `confidence`: provisional heuristic confidence in the range 0-1
- `model_version`
- `observed_at`
- `density`

Unknown roads return HTTP 404.

## Gateway integration

Intern 1 should register the gateway route `/api/ai/predict/congestion` and forward the `road_id` plus the three optional observation fields without renaming them. The gateway should preserve the AI Engine status code and response body. The service does not call the gateway, preventing a routing loop.

The current workspace does not contain Intern 1's gateway or Intern 2's `/traffic/live` endpoint, so live integration remains an environment handoff rather than a claim of completed end-to-end integration.

## Milestone 2 plan

- Replace the CSV fallback with the live feed client or a gateway-provided observation payload.
- Acquire road capacities and reviewed labels.
- Train and evaluate a leakage-safe scikit-learn baseline.
- Compare the baseline with gradient boosting and TensorFlow only if the data volume justifies it.
- Preserve the response contract and update `model_version` when the trained pipeline is deployed.
