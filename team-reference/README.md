# TrafficVision

The final target runs one FastAPI application with a static HTML frontend. It does not start the source project's seven microservices, PostgreSQL, or Redis.

## Setup

Use Python 3.11. From `team-reference\backend`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Before starting the API, configure `TRAFFICVISION_AUTH_SECRET` with a stable random signing secret and `TRAFFICVISION_DEFAULT_ADMIN_PASSWORD` with a unique initial admin password in the process environment or a secret manager. The API does not create a default admin when the password is unset. Do not commit `.env` files or `data\users.json`; both are local-only.

Then start from the `TrafficVision` folder:

```powershell
.\start_all.ps1
```

The scripts are safe to repeat. They reuse a healthy service and refuse to stop an unrelated process occupying a required port. Stop only verified TrafficVision services with:

```powershell
.\stop_all.ps1
```

## Services

| Service | URL |
|---|---|
| Dashboard | http://127.0.0.1:5500/dashboard.html |
| FastAPI | http://127.0.0.1:8001 |
| Swagger | http://127.0.0.1:8001/docs |
| Health | http://127.0.0.1:8001/health |

The integrated API includes traffic, historical records, aggregation, congestion prediction, peak-hour statistics, delay estimates, route ranking, OSRM geometry routes, alerts, anomaly proxies, analytics, reports, authentication, and model evaluation.

## Data And Storage

Traffic history and model inputs use `data\external\traffic_readings_export.csv`, an imported synthetic/demo snapshot of 40,320 rows across roads `R001`-`R005`. It is not a real-time sensor feed. Refreshing the dashboard re-queries this file through FastAPI.

User password hashes remain in `data\users.json`. Refresh sessions, event alerts, read state, road conditions, and OSRM route cache are stored in `.trafficvision\state.sqlite3`. Traffic history is not duplicated into that state database.

## AI Model

The active artifact is `aiml\models\source_ml_v2.joblib`, model `ml-v2`, trained with scikit-learn `1.9.1`. The original `congestion_model.joblib` is retained but inactive. The API recomputes evaluation using the artifact's train-only evaluator on its chronological holdout and reports precision, recall, F1, confusion matrix, feature importance, and leakage checks. Labels are generated/demo labels and are not real-world accuracy evidence.

AI mismatch alerts are anomaly proxies, not confirmed accidents. Coordinate routes use OSRM and display returned geometry; route congestion is not map-matched because this dataset has no road-to-coordinate mapping. The road-sequence ranking API does use observed road lengths and model congestion estimates.

## Tests

With the backend environment activated:

```powershell
python -m pytest api -q
```

From `team-reference\aiml`:

```powershell
..\backend\.venv\Scripts\python.exe -m pytest src -q
```
