# Milestone 4 — Day 2 Summary (Intern 5: QA, DevOps & Release Engineering)

Date: 2026-10-04

## Checkpoints (SRS §11.5, §12.2 "Deploy-Pipeline Ready")

- [x] CI/CD pipeline has a deploy stage: lint → build → test → deploy (`.github/workflows/ci.yml`)
- [x] Production compose and env template ready (`docker-compose.prod.yml`, `.env.prod.example`)
- [x] Post-deploy health gate + automatic rollback
- [x] Pipeline skeleton handed to Intern 1 (SRS §8 dependency, due Day 2)
- [ ] Pipeline run green on GitHub: blocked by DEF-M4-001 (lint) and DEF-M4-003 (code not pushed)
- [ ] Deploy executed against a real VM: Day 3, waiting on the target decision and secrets

## What was built

See `cicd_pipeline.md` for the full design and setup steps.

- **build** job (new): matrix builds `backend`, `analytics` and `ai` images and pushes them to GHCR
  with immutable `sha-<commit>` tags, only from `main`.
- **deploy** job (new): runs on `main` after lint/build/tests pass. It uploads the prod compose file
  over SSH, pulls the exact images, restarts and runs the health gate. If the gate fails it rolls back
  to the previous tag. It is skipped with a warning while secrets are unset.
- **docker-compose.prod.yml**: no `--reload` or bind mounts, Postgres/Redis not published, memory
  limits (~2 GB total), log rotation, and it fails fast if `IMAGE_PREFIX`, `IMAGE_TAG` or
  `POSTGRES_PASSWORD` is missing.
- **.env.prod.example**: the production env var list (DB, Redis, JWT, alert service key, maps key, CORS).
  `.gitignore` now ignores `.env.prod`.
- **post_deploy_health.py**: stdlib-only. Checks backend `/health`, analytics `/`, AI `/health`
  and one real gateway read (`/api/v1/traffic/live`).

## Verification (local)

| Check                                                                                                         | Result                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `actionlint 1.7.12 .github/workflows/ci.yml`                                                                  | ✅ 0 findings                                                                                                           |
| `docker compose -f docker-compose.prod.yml config -q` with `IMAGE_PREFIX`/`IMAGE_TAG`/`POSTGRES_PASSWORD` set | ✅ valid. Images resolve to `ghcr.io/<owner>/trafficvision-{backend,analytics,ai}:sha-…`. Only 8000/8001/8010 published |
| Same without `IMAGE_PREFIX`                                                                                   | ✅ fails fast: `required variable IMAGE_PREFIX is missing a value`                                                      |
| `post_deploy_health.py` with nothing running                                                                  | ✅ 0/4, exit 1 (would trigger rollback)                                                                                 |
| `post_deploy_health.py` against the 3 services started locally with uvicorn                                   | ✅ 4/4, exit 0. Evidence: `local_health_check_results.json`                                                             |
| QA lint (`flake8 QA`, `black --check QA`)                                                                     | ✅ 0 / clean                                                                                                            |
| `pytest -q` (the pipeline's test stage)                                                                       | ✅ 114 passed, 46 skipped, 5 xfailed                                                                                    |
| `docker build` of the 3 images                                                                                | ⏸ not run locally (DEF-M4-002, Docker engine down). CI builds them on the first push                                    |

## Blockers for Day 3

1. **DEF-M4-003**: push the code to GitHub so the pipeline runs for real.
2. **DEF-M4-001**: lint must be green in backend, analytics and frontend, or deploy never starts.
3. **Team Lead**: confirm the VM provider and create the account. Then I set the `production` secrets.
4. **DEF-M4-004**: Intern 1 adds a backend `.dockerignore` (`.env`, `.venv`, `*.db`).
5. **DEF-M4-005**: Intern 4 makes the API base URL configurable before hosting the frontend.
