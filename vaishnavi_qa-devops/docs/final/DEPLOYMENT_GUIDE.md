# TrafficVision AI — Deployment Guide (Milestone 4)

## Live deployment (current)

Everything runs as **one Render web service**, `https://trafficvision-ai-i8e2.onrender.com`,
built from `Backend_Iswarya/` in `deekshuu09-sudo/TrafficVision-AI` (`main`, Docker,
auto-deploy on push):

| Path          | What                                              | Code in `Backend_Iswarya/`        |
| ------------- | ------------------------------------------------- | --------------------------------- |
| `/`           | Web app (redirects to `/Login.html`)              | `Front-end/` (copy of `Frontend_Vennela`) |
| `/api/v1/...` | Gateway: Auth, Monitoring, Prediction, Route, Alerts | `app/`                         |
| `/analytics`  | Analytics (Intern 2)                              | `services/analytics/`             |
| `/ai-engine`  | AI Engine (Intern 3)                              | `ai-engine/`                      |
| `/docs`       | Swagger UI (also `/analytics/docs`, `/ai-engine/docs`) |                              |

Why one service: the free tier gives one URL per service and the frontend already calls
Analytics and the AI Engine through `<gateway>/analytics` and `<gateway>/ai-engine`.
`app/subapps.py` mounts both apps unchanged. On startup the backend creates any missing
tables and loads reference data when they are empty (`app/bootstrap.py`,
`prepare_analytics_data` — same steps as `QA/milestone4/day3/setup_production_db.py`), so a
fresh Postgres needs no manual seeding. Memory ≈ 230 MB of the 512 MB limit.

Render environment variables: `DATABASE_URL` (External URL + `?sslmode=require`),
`JWT_SECRET_KEY`, `ALERT_SERVICE_KEY`, `CORS_ALLOWED_ORIGINS=https://trafficvision-ai-i8e2.onrender.com`,
`PORT=8000`; `REDIS_URL` optional.

Run the live suites against it:

```powershell
$env:BACKEND_URL="https://trafficvision-ai-i8e2.onrender.com"
$env:WEB_URL=$env:BACKEND_URL
$env:ANALYTICS_URL="$env:BACKEND_URL/analytics"
$env:AI_URL="$env:BACKEND_URL/ai-engine"
```

The multi-service layout below (`render.yaml`, one service per intern) is the original
plan and still works if the team moves to a paid plan.

---

Production runs entirely on free tiers:

| Part                                   | Where                                | Notes                                                 |
| -------------------------------------- | ------------------------------------ | ----------------------------------------------------- |
| API gateway (`tv-team1-backend`)       | Render free web service (Docker)     | Auth, Monitoring, Prediction, Route Analysis, Alerts  |
| Analytics (`tv-team1-analytics`)       | Render free web service (Docker)     | Trends, heatmap, CSV reports, traffic history         |
| AI Engine (`tv-team1-ai`)              | Render free web service (Docker)     | Anomalies, recommendations, model predictions         |
| Frontend (`tv-team1-web`)              | Render static site                   | The 8 HTML pages + `api.js`                           |
| PostgreSQL                             | Render Postgres (set up by Intern 2) | Free tier expires 30 days after creation, see Backups |
| Redis                                  | Upstash free                         | Cache for live traffic and analytics                  |
| CI/CD, images, backups, live test runs | GitHub Actions + GHCR                | `ci.yml`, `db-backup.yml`, `live-qa.yml`              |

Everything is defined in the repo: `render.yaml` (services), `.github/workflows/ci.yml`
(lint → build → test → deploy), `.github/workflows/db-backup.yml` (daily backup + restore
test), `.github/workflows/live-qa.yml` (Day 3–6 test suites on demand).

**Free-tier limits to remember:** 512 MB RAM and a shared CPU per service; a service
sleeps after 15 minutes without traffic and takes ~1 minute to wake; 750 instance-hours
per month for the whole workspace (don't keep all services awake 24/7).

---

## 1. One-time setup (≈ 30 minutes)

### 1.1 Your own copy of the repo

The team repo belongs to the mentor account, so Render can't be connected to it and you
can't add secrets there. Deploy from a fork:

1. On GitHub open the team repo → **Fork** → your account.
2. Push the Team-1 branch to the fork's `main` (CI deploys only from `main`):
   ```powershell
   git remote add fork https://github.com/<your-user>/Traffic-Prediction-and-Intelligent-Congestion-Management-.git
   git push fork Team-1:main
   ```
3. Fork → **Settings → Actions → General** → allow actions; **Settings → Environments →
   New environment** → `production`.

### 1.2 Database (Intern 2's Render Postgres)

1. Ask Intern 2 for the **External Database URL** (Render dashboard → the database →
   Connections). Add `?sslmode=require` at the end if it isn't there.
2. Check what was migrated — this changes nothing:
   ```powershell
   pip install psycopg2-binary pandas python-dotenv
   $env:DATABASE_URL="postgresql://USER:PASS@HOST.oregon-postgres.render.com/DB?sslmode=require"
   python QA/milestone4/day3/setup_production_db.py --check
   ```
3. If it reports missing tables/columns or empty tables (for example `traffic_readings`,
   which the live-traffic endpoints read), agree with Intern 2 and then fill only what's
   missing (existing data is never touched; each table loads only when empty):
   ```powershell
   python QA/milestone4/day3/setup_production_db.py
   ```

### 1.3 Redis (Upstash)

[console.upstash.com](https://console.upstash.com) → Create database → region
**us-west-2 (Oregon)** → copy the **`rediss://` URL** (Connect → Redis URL).

### 1.4 Render services

1. [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint** → pick your
   fork → Render reads `render.yaml`.
2. It asks for `DATABASE_URL` (step 1.2) and `REDIS_URL` (step 1.3). `JWT_SECRET_KEY` and
   `ALERT_SERVICE_KEY` are generated for you.
3. **Apply.** The first build takes 10–20 minutes on the free tier.
4. Note the four URLs. If any service got a different subdomain than
   `trafficvision-<name>.onrender.com`, update:
   - `Front-end(m-3) (1)/Front-end/api.js` → `PRODUCTION_URLS`
   - Render env group `trafficvision-shared` → `CORS_ALLOWED_ORIGINS`
   - `tv-team1-analytics` → `ALERT_API_URL`, `tv-team1-ai` → `TRAFFIC_API_URL`
   - GitHub repo **variables** `BACKEND_URL`, `ANALYTICS_URL`, `AI_URL`, `WEB_URL`

### 1.5 GitHub secrets (fork → Settings → Environments → production)

| Secret               | Value                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------- |
| `RENDER_API_KEY`     | Render → Account Settings → API Keys → Create                                             |
| `RENDER_SERVICE_IDS` | `backend=srv-…,analytics=srv-…,ai=srv-…,web=srv-…` (each service → Settings → Service ID) |
| `DATABASE_URL`       | Same as step 1.2 (backup workflow + QA account promotion)                                 |
| `ALERT_SERVICE_KEY`  | Render env group value (lets the QA suites test the alert producer path)                  |

---

## 2. Deploying

Push to `main` of the fork. `ci.yml` then runs:

```
lint ─┐
build ├─► deploy: Render API deploys this exact commit to all 4 services
tests ┘          ► waits until every service is "live"
                 ► health gate (QA/milestone4/day2/post_deploy_health.py)
                 ► live smoke test (QA/milestone4/day3/smoke_test_live.py)
                 ► any failure → automatic rollback to the previous live deploy
```

Manual run: Actions → CI/CD → Run workflow (branch `main`).
Manual rollback: Render dashboard → service → Events → previous deploy → **Rollback**, or
`python QA/milestone4/day3/render_deploy.py rollback --state deploy_state.json` with the
state file from the run's artifacts.

## 3. Testing the live system (Days 3–6)

From GitHub: **Actions → Live QA → Run workflow** → pick the suite. The report appears in
the run summary and as an artifact (commit the ones you keep into `QA/milestone4/dayN/`).

Or locally (PowerShell):

```powershell
$env:BACKEND_URL="https://trafficvision-ai-i8e2.onrender.com"
$env:ANALYTICS_URL="https://trafficvision-ai-i8e2.onrender.com/analytics"
$env:AI_URL="https://trafficvision-ai-i8e2.onrender.com/ai-engine"
$env:WEB_URL="https://trafficvision-ai-i8e2.onrender.com"
$env:ALERT_SERVICE_KEY="<from Render>"; $env:DATABASE_URL="<production URL>"
pip install selenium psycopg2-binary

python QA/milestone4/day3/smoke_test_live.py   --report QA/milestone4/day3/smoke_results.md
python QA/milestone4/day4/full_system_test.py  --report QA/milestone4/day4/full_system_test_report.md --json QA/milestone4/day4/full_system_results.json
python QA/milestone4/day4/selenium_ui_test.py  --browsers chrome,firefox,edge --report QA/milestone4/day4/selenium_ui_report.md --shots QA/milestone4/day4/screenshots
python QA/milestone4/day5/performance_check.py --report QA/milestone4/day5/performance_report.md --json QA/milestone4/day5/performance_results.json
python QA/milestone4/day6/final_regression.py  --stability-minutes 10 --report QA/milestone4/day6/final_regression_report.md
```

The same scripts run against the local Docker stack by pointing the URLs at
`http://127.0.0.1:8000/8001/8010` and a local static server.

## 4. Backups and restore

- **Automatic:** `db-backup.yml` runs daily at 02:00 IST: `pg_dump` → restore into a scratch
  Postgres → row counts compared table by table → dump kept 14 days as an artifact.
- **Manual restore** (also how to move off the free DB before its 30-day expiry):
  ```bash
  # download trafficvision-db-<stamp> from the workflow run, then:
  docker run --rm -v "$PWD:/b" postgres:18-alpine \
    pg_restore --no-owner --no-privileges --clean --if-exists -d "$NEW_DATABASE_URL" /b/trafficvision-<stamp>.dump
  ```
  Then set the new URL in Render's `trafficvision-shared` group and the GitHub secret.

## 5. Before the demo

1. Open the frontend and each API `/health` URL 2–3 minutes before (wakes the services).
2. Run the smoke suite (Actions → Live QA → smoke). Green = ready.
3. Demo accounts: register through the UI; promote operator/admin with
   `UPDATE users SET role='operator' WHERE email='…';` on the production DB.

## 6. Troubleshooting

| Symptom                                      | Cause / fix                                                                                        |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| First request takes ~60 s                    | Free service was asleep. Expected; wake services before demos.                                     |
| Browser console: CORS error                  | Frontend URL not in `CORS_ALLOWED_ORIGINS` (Render env group). Comma-separate several origins.     |
| Backend crashes: `No module named 'psycopg'` | Fixed in `app/database.py` (forces the psycopg2 driver). Make sure you deployed the latest commit. |
| Live traffic empty / 500                     | `traffic_readings` or `roads` missing → `setup_production_db.py --check`.                          |
| Deploy stage "skipped"                       | `RENDER_API_KEY` / `RENDER_SERVICE_IDS` not set in the `production` environment.                   |
| Service "suspended"                          | 750 free instance-hours used up; wait for the monthly reset or reduce keep-alive pings.            |
| Model warnings in logs                       | scikit-learn must stay `1.9.0` (pinned in backend `requirements.txt`).                             |
