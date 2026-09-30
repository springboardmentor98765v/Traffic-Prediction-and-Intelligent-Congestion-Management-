# TrafficVision AI — Deployment Readiness Checklist

> ## ⚠️ PLANNING ONLY — FOR MILESTONE 4 USE
>
> This is a planning document. **No deployment activity was performed in Milestone 3**, and
> none should be performed from this checklist until Milestone 4 starts (SRS §4, §9, §15).
> Please raise this as a reminder at the Day 7 stand-up.

Prepared by: Intern 5 (QA / DevOps / Release Engineering) · Date: 2026-09-25
Based on: the Milestone 3 final validation cycle (`m3_qa_signoff_report.md`) and a read-through of
the current repo (`Team-1` working tree).

**Status key:** ✅ Ready · ⚠️ Partly ready · ❌ Not ready · ❓ Decision needed

## 0. Entry gate: Milestone 3 must be closed first

| #   | Item                                                    | Current state                                                                                                                                                                                                                                                                       | Owner          | Status |
| --- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------ |
| 0.1 | Milestone 3 QA sign-off granted                         | Not signed off: 6 High defects open (retest 2026-09-26: 005, 017, 021, 023, 024, 025) (see sign-off report)                                                                                                                                                                         | QA + Team Lead | ❌     |
| 0.2 | No open Critical/High defects (`docs/QUALITY-GATES.md`) | Open: DEF-M3-005, 012, 014, 017, 021, 023 (+ 004, 009, 020 Medium/High)                                                                                                                                                                                                             | All            | ❌     |
| 0.3 | CI green on the release branch                          | `tests` job passes locally. `code-quality` job red (repo-wide: flake8 428, black 67 files, ESLint 9 errors, Prettier 74 files, 1 inline-script syntax error; QA-owned files clean; see Day 6 code-quality report). Repo content not yet committed/pushed, so CI has never run on it | QA + all       | ❌     |
| 0.4 | AI Insights scope decided                               | Service not delivered (DEF-M3-017): deliver or descope formally                                                                                                                                                                                                                     | Team Lead      | ❓     |

## 1. Code, build and images

| #   | Item                                | Current state                                                                                                                                                                                                             | Owner        | Status |
| --- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ------ |
| 1.1 | One agreed source layout            | Backend in `backend (1)/backend/Intern_AI AND ML` (spaces, brackets); duplicate copies in `AIML/`, `TrafficVision-AI 3/`, `backend (1)/.../data/M2_Day7…`, `vaishnavi_qa-devops/`. Rename to `backend/` and delete copies | Team Lead    | ❌     |
| 1.2 | Dependencies pinned                 | Backend `requirements.txt` mostly unpinned (fastapi, uvicorn, sqlalchemy, pandas, **scikit-learn** – model pickled with 1.9.0, container has 1.7.2, DEF-M2-008). Generate a lock/constraints file                         | AI + Backend | ❌     |
| 1.3 | A Dockerfile per deployable service | Gateway ✅. Analytics ❌ (reuses the backend image in dev). AI Insights ❌ (no service)                                                                                                                                   | Data, AI     | ⚠️     |
| 1.4 | Production image hygiene            | Gateway image runs as root, has build tools left in, no `HEALTHCHECK`. Dev compose uses `--reload` and bind mounts, which must not be used in prod                                                                        | Backend + QA | ❌     |
| 1.5 | Image versioning                    | Only `trafficvision-backend:dev`. Need immutable tags (git SHA / semver) and a registry                                                                                                                                   | QA/DevOps    | ❌     |
| 1.6 | Production compose / manifests      | `docker-compose.yml` is stale: builds `./backend` (doesn't exist), has an obsolete `version:` key, hard-coded `trafficpass`, dev bind mount, and no Analytics/AI services                                                 | QA/DevOps    | ❌     |

## 2. Configuration and secrets

| #   | Item                                           | Current state                                                                                                                                                                       | Owner          | Status |
| --- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------ |
| 2.1 | JWT signing key from the environment           | **Hard-coded literal** in `app/security/config.py` / `jwt.py` (DEF-M3-021). Move to `JWT_SECRET_KEY` env, fail if missing, rotate                                                   | Backend        | ❌     |
| 2.2 | DB / Redis credentials from the environment    | Dev defaults `change_me` / `trafficpass`; `seed_db.py` and `database.py` default URLs contain passwords. Use a secret store / env only                                              | Backend + Data | ❌     |
| 2.3 | `.env` files never committed                   | ✅ Root `.gitignore` covers `.env`, `*.env`; 4 local `.env` files exist and are ignored. Keep `.env.example` templates up to date                                                   | All            | ✅     |
| 2.4 | CORS restricted to the real frontend origin    | Gateway allows `*` with credentials. Analytics has none (DEF-M3-014). Set explicit origins per environment                                                                          | Backend + Data | ❌     |
| 2.5 | Frontend API URLs configurable per environment | LAN IP removed and ports fixed (DEF-M3-013 fixed 2026-09-25), but `127.0.0.1:8000/8001/8010` are still hard-coded in `api.js`. Use one config file / build variable per environment | Frontend       | ⚠️     |
| 2.6 | Token lifetime / refresh policy agreed         | Access token 60 min. Refresh exists. Confirm values for production                                                                                                                  | Backend        | ❓     |

## 3. Data and database

| #   | Item                          | Current state                                                                                                                                                                                         | Owner          | Status |
| --- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------ |
| 3.1 | Schema migrations             | Gateway uses `Base.metadata.create_all` at startup; Analytics tables from hand-run SQL (`Data/sql/*.sql` via `analytics_setup.sh`). Adopt Alembic (or ordered SQL migrations) with a single run order | Backend + Data | ❌     |
| 3.2 | Initial data load procedure   | Documented for dev (`QA/milestone3/day6/analytics_setup.sh`, idempotent). Needs a production version (real data source, not synthetic)                                                                | Data           | ⚠️     |
| 3.3 | Indexes for analytics queries | ✅ Query plans use `idx_traffic_history_latest`; 4-week queries 0.4–1.6 ms in DB, < 0.4 s end-to-end                                                                                                  | Data           | ✅     |
| 3.4 | Backups and restore test      | None defined. Define schedule, retention, and a restore drill                                                                                                                                         | QA/DevOps      | ❌     |
| 3.5 | Timezone convention           | Mixed: naive IST (monitoring), naive UTC (alerts), UTC+offset (analytics) (DEF-M3-016, 010). Agree "store UTC, return ISO-8601 with offset"                                                           | Backend + Data | ❌     |

## 4. Security

| #   | Item                                                         | Current state                                                                                                                           | Owner     | Status |
| --- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | --------- | ------ |
| 4.1 | Server-side RBAC on every endpoint                           | Auth, Route ✅. **Alerts ❌** (no JWT, `?role=` trusted: DEF-M3-005/012). Traffic/Predict/Analytics are public; confirm that's intended | Backend   | ❌     |
| 4.2 | No client-side auth bypass                                   | ✅ Fixed 2026-09-25 (DEF-M3-019): login with the API unreachable now shows "Server unreachable" and creates no session                  | Frontend  | ✅     |
| 4.3 | HTTPS/TLS termination                                        | Not designed yet (reverse proxy / platform TLS)                                                                                         | QA/DevOps | ❌     |
| 4.4 | Rate limiting / abuse protection on login and alert creation | None                                                                                                                                    | Backend   | ❌     |
| 4.5 | Dependency vulnerability scan                                | Not run. Add `pip-audit` / `npm audit` to CI                                                                                            | QA/DevOps | ❌     |
| 4.6 | Public sign-up can't self-grant roles                        | ✅ Verified (`role: admin` in register → PUBLIC), regression test `tests/test_day4_api.py`                                              | —         | ✅     |

## 5. Reliability and performance

| #   | Item                                                          | Current state                                                                           | Owner     | Status |
| --- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------- | --------- | ------ |
| 5.1 | Health checks on every service                                | Gateway `/health` ✅, Analytics `/` ✅ (compose healthchecks). AI ❌                    | All       | ⚠️     |
| 5.2 | Degrades gracefully when Redis is down                        | Gateway ✅ (all calls 200). **Analytics trends/heatmap hang 90 s+** (DEF-M3-020)        | Data      | ❌     |
| 5.3 | Degrades gracefully when the external maps API (OSRM) is down | `/optimize`, `/travel-time` ✅. `/alternate` returns 500 (DEF-M3-004)                   | Backend   | ❌     |
| 5.4 | Alert delivery latency                                        | ✅ 100/100 delivered, 0 lost, p95 213 ms (target < 1 s)                                 | Backend   | ✅     |
| 5.5 | Analytics performance at 4 weeks                              | ✅ cold < 0.4 s, warm ~50 ms, all < 2 s target                                          | Data      | ✅     |
| 5.6 | Load test at production-like volume                           | Not done (only 4 weeks × 6 roads). Plan a load test with realistic road count / history | QA        | ❌     |
| 5.7 | Restart policy and resource limits                            | `restart: unless-stopped` in dev; no CPU/memory limits                                  | QA/DevOps | ⚠️     |

## 6. Observability and operations

| #   | Item                                             | Current state                                                           | Owner          | Status |
| --- | ------------------------------------------------ | ----------------------------------------------------------------------- | -------------- | ------ |
| 6.1 | Structured application logs                      | Uvicorn access logs + `print` only                                      | Backend + Data | ❌     |
| 6.2 | Metrics and alerting on service health           | None                                                                    | QA/DevOps      | ❌     |
| 6.3 | Runbook (start/stop, data load, common failures) | Partial: `docs/SETUP-GUIDE.md`, compose comments, QA reproduce sections | QA/DevOps      | ⚠️     |

## 7. Frontend release

| #   | Item                                  | Current state                                                                                                                                                              | Owner    | Status |
| --- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------ |
| 7.1 | Production CSS build                  | Uses `cdn.tailwindcss.com` (browser console: "should not be used in production"). Build Tailwind at compile time                                                           | Frontend | ❌     |
| 7.2 | Mock-data fallbacks off in production | Pages silently fall back to mock data on any API error (hid DEF-M3-013/017/018). Must be dev-only, or show a visible error                                                 | Frontend | ❌     |
| 7.3 | Pages use live APIs                   | Login, dashboards, Route, bell, Alerts list ✅ (DEF-M3-018 fixed). Operator dashboard ❌ (DEF-M3-023). Analytics page ❌ until CORS (DEF-M3-014). AI panel ❌ (DEF-M3-017) | Frontend | ❌     |

## 8. Release process and test gates

| #   | Item                                             | Current state                                                                                                                                                                                  | Owner          | Status |
| --- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------ |
| 8.1 | Automated suites ready to re-run against staging | ✅ `pytest -q` (unit + live), `stack_smoke_test.py`, `alert_delivery_check.py`, `integration_cycle.py`, `frontend_e2e.py`, `analytics_perf_cache_check.py`. All take a base URL / env override | QA             | ✅     |
| 8.2 | CI has no deployment stage (M3 rule)             | ✅ CI is lint/build/test only. A deploy stage is Milestone 4 work                                                                                                                              | QA/DevOps      | ✅     |
| 8.3 | Staging environment                              | Not defined                                                                                                                                                                                    | Team Lead + QA | ❌     |
| 8.4 | Rollback plan                                    | Not defined. Needs versioned images (1.5) plus DB migration down-steps (3.1)                                                                                                                   | QA/DevOps      | ❌     |
| 8.5 | Release notes + go/no-go meeting                 | Template to prepare in M4; M3 sign-off report is the input                                                                                                                                     | QA + Team Lead | ❌     |

## 9. Summary for the Milestone 4 kickoff

- **Ready now (8):** `.env` hygiene, no client-side auth bypass, analytics indexes, sign-up role protection, alert
  latency, analytics performance, automated test suites, CI without a deploy stage.
- **Must fix in code before any deployment:** the 6 open High defects, plus DEF-M3-020, DEF-M3-022 (Redis
  timeout) and DEF-M3-004. Those are Milestone 3 carry-overs.
- **New Milestone 4 engineering work:** folder cleanup, pinned deps, per-service Dockerfiles,
  production compose/manifests, secrets management, migrations, TLS, backups, logging and
  metrics, staging, rollback.
- **Decisions needed from the Team Lead:** AI Insights scope (0.4), token lifetime (2.6),
  which endpoints are intentionally public (4.1).

_Reminder: planning only. Marked for Milestone 4 use. No deployment was performed in
Milestone 3._
