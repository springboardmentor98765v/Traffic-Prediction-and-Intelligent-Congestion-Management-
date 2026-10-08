# Milestone 4 Day 3 — Deploy full stack to cloud + smoke tests

**Target chosen:** Render free tier (3 Docker web services + static site) with Intern 2's
Render Postgres and Upstash Redis. Docker-on-VM (`docker-compose.prod.yml`) stays as the
fallback. Guide: `docs/final/DEPLOYMENT_GUIDE.md`.

## Built today

| Deliverable                                                              | File                                                                                                                                           |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Render Blueprint (4 services, shared secrets, CORS, health checks)       | `render.yaml`                                                                                                                                  |
| CI deploy stage → Render API, exact commit, wait for live, auto-rollback | `.github/workflows/ci.yml`, `day3/render_deploy.py`                                                                                            |
| Health gate for per-service HTTPS URLs                                   | `day2/post_deploy_health.py --url …`                                                                                                           |
| Live smoke test (availability, DB, JWT, model, Redis, frontend, CORS)    | `day3/smoke_test_live.py`                                                                                                                      |
| Production DB setup + read-only `--check`                                | `day3/setup_production_db.py`                                                                                                                  |
| Daily backup with restore verification                                   | `.github/workflows/db-backup.yml`                                                                                                              |
| One-click live test runs (smoke/full/UI/perf/regression)                 | `.github/workflows/live-qa.yml`                                                                                                                |
| Production fixes in service code                                         | CORS from env, `REDIS_URL`, `DATABASE_URL` in analytics, psycopg2 driver pin, scikit-learn 1.9.0, `.dockerignore` ×3, `api.js` production URLs |

## Local production rehearsal (2026-10-07)

Exact Render images, 512 MB memory caps, Postgres 17, password-protected Redis:

- All 4 services healthy. Memory: backend 154 MB, AI 131 MB, analytics 53 MB.
- DB setup: 6 tables loaded (roads 6, traffic_readings 1446, traffic_history 4032,
  road_conditions 9, hourly 4032, daily 174); re-running changes nothing.
- Smoke: 29/30. The 1 fail is the `/` → Login rewrite, which only Render's rewrite rule
  provides (local nginx has none). 2 SKIP are live-only checks (HTTPS, production URL in `api.js`).
- Backup: dump → restore → 7/7 tables matched.
- Found and fixed before go-live: DEF-M4-010 (backend crash with provider DB URLs),
  DEF-M2-008 (model/library version mismatch).

## Pending (live)

- [ ] Fork + Render Blueprint + secrets (guide §1)
- [ ] `setup_production_db.py --check` on Intern 2's DB (DEF-M4-015)
- [ ] First CI deploy green; smoke report saved here as `smoke_results.md`
- [ ] Live URLs shared with Interns 1–4
