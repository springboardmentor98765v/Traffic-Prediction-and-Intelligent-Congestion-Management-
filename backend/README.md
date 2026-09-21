# TrafficVision AI - Milestone 1 Backend Starter

This is an independent M1 starter until the Team-5 repository link is available. It preserves the SRS paths:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `GET /api/v1/traffic/live`, `/road/{road_id}`, `/density` (gateway integration routes)
- `GET /api/v1/predict/congestion?road_id={id}` (gateway integration route)

## Run locally

1. Install Python 3.12+, then run `pip install -r requirements.txt`.
2. Run the Auth service: `uvicorn app.main:app --app-dir services/auth --port 8001 --reload`.
3. Run the AI Engine: `uvicorn app.main:app --app-dir services/ai-engine --port 8003 --reload`.
4. Run the gateway in a second terminal: `uvicorn app.main:app --app-dir services/gateway --port 8000 --reload`.
5. Open `http://localhost:8001/docs` for Auth Swagger and `http://localhost:8000/docs` for the Gateway.
6. Run tests: `pytest`.

For PostgreSQL and Redis, create a `.env` from `.env.example`, set a real `JWT_SECRET`, and run `docker compose -f docker-compose.dev.yml up --build`.

## Team integration remaining

The integrated AI Engine is available at `PREDICTION_SERVICE_URL` and serves the `/api/v1/traffic/*` paths by default when `TRAFFIC_SERVICE_URL` is not overridden. A dedicated traffic-monitoring service can still be selected through that environment variable. Intern 5 owns CI, Compose validation, and the final integration test cycle.

Before merging into Team-5's repository, compare filenames, dependency versions, and any existing migrations; do not overwrite teammates' monitoring/prediction code.

## Milestone 2 backend increment

The Route Analysis service is available at port `8004` and preserves the M2 contracts: `GET /api/v1/route/optimize`, `/alternate`, `/travel-time`, and `/conditions`. It uses the free OSRM public routing service built from OpenStreetMap data. Start it locally with `python -m uvicorn app.main:app --app-dir services/route-analysis --port 8004` and view its Swagger page at `http://127.0.0.1:8004/docs`.

Example: `GET /api/v1/route/optimize?origin=12.9716,77.5946&destination=12.9352,77.6245`.
