# Day 2 — Local Dev Environment Extension (Milestone 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Per SRS Section 10.5 Day 2: "Extend `docker-compose.dev.yml` to include the time-series store and the new Route Analysis / Prediction services; verify the full local stack still starts correctly."

## 1. Time-series store

`docker-compose.dev.yml`'s `postgres` service image changed from `postgres:16-alpine` to `timescale/timescaledb:2.17.2-pg16` — a drop-in PostgreSQL replacement with the TimescaleDB extension available (`CREATE EXTENSION IF NOT EXISTS timescaledb;`). Ready for Intern 2's historical-data tables to become hypertables without another environment change once her schema is merged in (see integration note in the Day 3/Day 6 work).

## 2. Route Analysis / Prediction services

No new container needed — Route Analysis and Prediction are routers inside the single `backend` FastAPI app (`app/routes/route_analysis.py`, `app/routes/predict.py`), already served by the existing `backend` service in this file. Architecturally this requirement is already satisfied by the single-gateway pattern the backend intern used.

## 3. Verify the full local stack starts — 2 real defects found and fixed

This was not a formality — the stack genuinely did not start on first attempt, for reasons that had nothing to do with the TimescaleDB change:

### DEF-M2-014a: `.env.dev` never existed
`docker-compose.dev.yml` requires `env_file: .env.dev`, but only `.env.dev.example` existed in the repo. This means **this file has likely never successfully brought up a stack for anyone**, at any point before today. Fixed by creating `.env.dev` from the example, per the README's own documented setup steps (`cp .env.dev.example .env.dev`).

### DEF-M2-014b: `DATABASE_URL` pointed the backend at itself
Once `.env.dev` existed, the `backend` service still hung indefinitely on startup with no error logged. Root cause: the `environment:` block's fallback default was:
```
DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg2://traffic:change_me@localhost:5432/trafficvision}
```
Compose's `${VAR:-default}` substitution reads from a root-level `.env` file (which doesn't exist) or the shell — **not** from `.env.dev` (that's only used via `env_file:`, a separate mechanism). So the default always won, and `localhost` inside the backend's own container refers to itself, not the `postgres` service — the backend was trying to connect to a database that was never there. Confirmed via `docker exec trafficvision-backend-dev env`, which showed exactly this wrong value. Fixed by correcting the fallback host to `postgres`.

### Verification
```
docker compose -f docker-compose.dev.yml up -d --build
```
All 3 containers come up healthy:
```
trafficvision-backend-dev:   Up
trafficvision-postgres-dev:  Up (healthy)
trafficvision-redis-dev:     Up (healthy)
```
Backend logs show a clean startup for the first time:
```
INFO:     Application startup complete.
```
```
curl http://localhost:8000/health
→ HTTP 200  {"status":"ok"}
```

Both fixes logged as **DEF-M2-014** in [defect_tracker.md](../day1/defect_tracker.md) (Fixed).

## Overall Status
Day 2 is now genuinely complete, with proof: the stack builds and starts cleanly end-to-end, for the first time. Note this only proves the **environment** works — the known API defects (DEF-M2-002/003/004/005) are still present in the running backend; starting cleanly is not the same as the endpoints being correct. Historical Data (Intern 2's service) is still not merged into this stack's `backend` container — see the Day 3/Day 6 integration note.
