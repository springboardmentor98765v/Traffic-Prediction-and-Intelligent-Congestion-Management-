# TrafficVision AI — Milestone 4 Test & Deployment Plan

Prepared by: Intern 5 (QA, DevOps & Release Engineering) · Date: 2026-10-04
Input: `QA/milestone3/day7/deployment_readiness_checklist_M4.md`, Milestone 4 SRS
(§4, §6–§12), M3 status `QA/milestone3/status_update.md`.

## 1. Goal

Take the M1–M3 system live on a free-tier cloud target through a CI/CD pipeline with a real
deploy stage. Then prove on the live system that every feature from M1 to M3 still works and is
fast enough. The milestone closes with a regression sign-off, final docs and a live demo
(FR-05 to FR-08).

## 2. Scope

| In scope (live system)                                                 | Out of scope                                                 |
| ---------------------------------------------------------------------- | ------------------------------------------------------------ |
| Auth/RBAC, live monitoring (M1)                                        | New features or new REST APIs (contracts are frozen, SRS §7) |
| Prediction, route analysis, maps (M2)                                  | Paid cloud tiers, Kubernetes                                 |
| Alerts, analytics, AI insights (M3)                                    | Load tests above free-tier capacity                          |
| CI/CD lint → build → test → deploy (FR-05)                             |                                                              |
| Deployment, smoke, full-system, performance, regression (FR-06, FR-07) |                                                              |
| Final documentation package and demo (FR-08)                           |                                                              |

## 3. Deployment approach

| Decision        | Choice                                                                                                                                             | Why                                                                                                                                                                           |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Target          | **One free-tier Linux VM running Docker Compose** (AWS EC2 t2/t3.micro, Azure B1s or Oracle Always-Free). Team Lead to confirm                     | SRS 7.2 allows it. The stack already runs on Compose, so prod matches local. Render/Railway free tiers would split the 3 services + DB into separate apps with sleep timeouts |
| Images          | Built in CI, pushed to GitHub Container Registry as `trafficvision-{backend,analytics,ai}:sha-<commit>`                                            | Immutable tags (checklist 1.5) make rollback a one-line redeploy                                                                                                              |
| Prod stack file | `docker-compose.prod.yml` (repo root)                                                                                                              | Fixes checklist 1.4/1.6: no `--reload`, no bind mounts, DB/Redis not public, memory limits                                                                                    |
| Secrets         | GitHub `production` environment secrets (SSH, registry) + `.env` on the VM from `.env.prod.example`                                                | Nothing secret in git (checklist 2.1–2.3)                                                                                                                                     |
| Database        | Postgres/Timescale container on the VM by default. Switch to managed Postgres if Intern 2 chooses one (SRS 7.3) by changing `DATABASE_URL` only    | Keeps Day 3 unblocked either way                                                                                                                                              |
| Frontend        | Static hosting on Netlify/Vercel (Intern 4, SRS 7.5), pointed at the VM's gateway URL                                                              | Static HTML. No server needed                                                                                                                                                 |
| TLS             | HTTP on Day 3 for smoke testing. HTTPS via a reverse proxy (Caddy/Nginx) or platform TLS with Intern 1's gateway config before the Day 4 full test | Checklist 4.3                                                                                                                                                                 |
| Rollback        | Deploy job re-runs the previous `sha-` tag automatically if the post-deploy health check fails. Manual: re-run the workflow for an older commit    | Checklist 8.4                                                                                                                                                                 |
| Change control  | After Day 3 go-live, production changes go **only** through the pipeline (SRS 12.3)                                                                |                                                                                                                                                                               |

## 4. Entry gate — re-check of the M3 readiness checklist (2026-10-04)

| #   | Item                      | M3 Day 7 | Today        | Evidence / note                                                                                                                                                            |
| --- | ------------------------- | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.1 | M3 QA sign-off            | ❌       | ❌           | Still NO-GO (`status_update.md`). M4 starts with known carry-over defects (see `defect_tracker.md`)                                                                        |
| 0.3 | CI green                  | ❌       | ⚠️           | `tests` passes locally (114 passed, 46 skipped, 5 xfailed). `lint` still red: flake8 230 (backend) + 42 (analytics), Black 66 files, ESLint 42 errors. QA folder now clean |
| 1.3 | Dockerfile per service    | ⚠️       | ⚠️           | Backend ✅, AI ✅. Analytics reuses the backend Dockerfile (works, built by CI)                                                                                            |
| 1.4 | Prod image hygiene        | ❌       | ⚠️           | Prod compose fixed. Images still root + build tools, no `.dockerignore` (DEF-M4-004)                                                                                       |
| 1.5 | Image versioning          | ❌       | ✅ (Day 2)   | `sha-<commit>` tags in GHCR                                                                                                                                                |
| 1.6 | Prod compose              | ❌       | ✅ (Day 2)   | `docker-compose.prod.yml`, validated with `docker compose config`                                                                                                          |
| 2.1 | JWT key from env          | ❌       | ✅ in source | `app/security/config.py` now raises if `JWT_SECRET_KEY`/`SECRET_KEY` missing. DEF-M3-021 to be retested live                                                               |
| 2.4 | CORS restricted           | ❌       | ❌           | `allow_origins=["*"]` in `app/main.py`. Intern 1, Day 3                                                                                                                    |
| 2.5 | Frontend API URLs per env | ⚠️       | ❌           | `api.js` hard-codes `127.0.0.1:8000/8001/8010`. Intern 4 must change before Day 3                                                                                          |
| 3.4 | Backups + restore test    | ❌       | ❌           | Intern 2, Day 3                                                                                                                                                            |
| 4.3 | HTTPS                     | ❌       | ❌           | Section 3 above                                                                                                                                                            |
| 7.1 | Tailwind CDN in prod      | ❌       | ❌           | 8 pages still load `cdn.tailwindcss.com`. Intern 4, Day 2                                                                                                                  |

## 5. Day-by-day plan (Intern 5)

| Day | Activity                                                              | Output                                                            | Exit check                                                      |
| --- | --------------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| 1   | This plan, entry-gate re-check, defect carry-over                     | `day1/` docs                                                      | Plan shared with team                                           |
| 2   | CI/CD with deploy stage, prod compose, prod env template, health gate | `ci.yml`, `docker-compose.prod.yml`, `.env.prod.example`, `day2/` | Pipeline valid. Deploy stage runs (or reports "not configured") |
| 3   | Provision VM, set secrets, first deploy, run smoke tests              | Live URLs, smoke report                                           | Health gate 4/4. `stack_smoke_test.py --base-url <live>` passes |
| 4   | Full application testing on the live system                           | Full-system test report                                           | All M1–M3 suites rerun against live URLs                        |
| 5   | Performance and responsiveness checks                                 | Performance report + prioritised defect list                      | Thresholds in §7                                                |
| 6   | Final regression after fixes                                          | Regression report, stability sign-off                             | §8 exit criteria                                                |
| 7   | Final documentation package, demo prep                                | `docs/` final package, demo script                                | Final sign-off                                                  |

## 6. Test levels and the suites that will be reused

All the M1–M3 suites already take a base URL / env override (checklist 8.1), so the same
scripts run against the live host.

| Level                        | When          | Suite                                                                                                                     |
| ---------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Pipeline gate                | Every push/PR | `pytest -q`, analytics `pytest`, AI `pytest`, flake8/Black/ESLint/Prettier                                                |
| Post-deploy health           | Every deploy  | `QA/milestone4/day2/post_deploy_health.py` (fails the job → auto-rollback)                                                |
| Smoke                        | Day 3         | `QA/milestone3/day2/stack_smoke_test.py --base-url http://<host>:8000`                                                    |
| Full system / workflows      | Day 4         | M1 auth/RBAC tests, `QA/milestone3/day6/regression_m1_m2.py`, `day5/integration_cycle.py`, `day4/alert_delivery_check.py` |
| UI end-to-end, cross-browser | Day 4–5       | `QA/milestone3/day5/frontend_e2e.py` (Playwright: Chromium, Firefox, WebKit, mobile viewport) on the hosted frontend      |
| Performance                  | Day 5         | Latency sampling per endpoint (p50/p95), page load, alert delivery                                                        |
| Regression                   | Day 6         | Everything above, one full pass                                                                                           |

Key workflows to validate live (SRS 1.3): login → dashboard → live traffic → prediction →
route → alert → analytics, run once for each role (admin, operator, public user).

## 7. Performance thresholds (FR-07)

Free-tier hardware, so these are "acceptable live" targets, not stretch goals.

| Metric                                                | Target                                 |
| ----------------------------------------------------- | -------------------------------------- |
| `/health` on each service                             | < 500 ms                               |
| Gateway read APIs (traffic, predict, alerts list) p95 | < 1 s                                  |
| Route optimisation p95                                | < 3 s (external OSRM)                  |
| Analytics trends/heatmap, 4 weeks, p95                | < 2 s (M3 baseline < 0.4 s)            |
| Alert delivery                                        | < 1 s p95, 0 lost (M3 baseline 213 ms) |
| Frontend page load (first contentful paint, desktop)  | < 3 s                                  |
| Error rate during the perf run                        | < 1 %                                  |

## 8. Exit criteria (Day 6 / Day 7 sign-off)

- No open Critical or High defects (`docs/QUALITY-GATES.md`); Mediums have an owner and a decision.
- CI/CD green on `main`, including the deploy stage, for the release commit.
- Every key workflow (§6) passes on the live system for all three roles.
- §7 thresholds met, or each miss is documented and accepted by the Team Lead.
- Rollback has been exercised at least once.
- Final documentation package complete (architecture, APIs, deployment guide, runbook).

## 9. Dependencies (SRS §8)

| I need                                                                                | From       | By      | Status                     |
| ------------------------------------------------------------------------------------- | ---------- | ------- | -------------------------- |
| Production Dockerfiles / `.dockerignore`, CORS allow-list, env var contract confirmed | Intern 1   | Day 2–3 | Open                       |
| Prod DB connection string, schema + seed load, backup job                             | Intern 2   | Day 3   | Open                       |
| Versioned model artifact inside the AI image (`models/model-v1.joblib`)               | Intern 3   | Day 2   | Present in source; confirm |
| Frontend API base URL configurable, Tailwind built, host chosen                       | Intern 4   | Day 3   | Open                       |
| Deploy target decision + cloud account                                                | Team Lead  | Day 3   | **Decision needed**        |
| From me: pipeline with deploy stage                                                   | → Intern 1 | Day 2   | ✅ Delivered               |
| From me: live environment / URLs                                                      | → All      | Day 3–4 | Pending VM                 |

## 10. Risks

| Risk                                                                                 | Impact                     | Mitigation                                                                                           |
| ------------------------------------------------------------------------------------ | -------------------------- | ---------------------------------------------------------------------------------------------------- |
| Lint stage red repo-wide blocks every deploy                                         | No go-live                 | Each owner fixes their folder (`black .`, flake8). Tracked as DEF-M4-001. Gate is not being weakened |
| Code not committed/pushed: CI has never run on GitHub                                | Pipeline unproven          | Push to the team branch, then PR to `main` (DEF-M4-003)                                              |
| Docker engine unavailable on QA machine                                              | Can't build images locally | CI builds them. Local Docker Desktop to be fixed for Day 3 debugging (DEF-M4-002)                    |
| Free-tier VM has 1 GB RAM                                                            | OOM with 5 containers      | Memory limits in prod compose (≈2 GB total cap). Add 1–2 GB swap on the VM. Use managed DB if needed |
| M3 High defects still open (alerts RBAC, public sees Critical alerts, producers 401) | Fails exit criteria        | Fix in M4 Days 2–6 and retest live                                                                   |
