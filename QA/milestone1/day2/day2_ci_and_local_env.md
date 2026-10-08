# Day 2: CI Pipeline and Local Integration Environment

## 1. CI pipeline: `.github/workflows/ci.yml`

**Triggers:** `push` and `pull_request` on `main` and `develop`. **There is no deploy job** (SRS 7.4, 10.5).

| Job            | Steps                                                                                                                                                                                                           | Purpose             |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| `tests`        | Postgres 16 and Redis 7 service containers → install backend, analytics and AI requirements → `compileall` + `import app.main` (build check) → `pytest -q` (root testpaths) → analytics suite → AI engine suite | Build and test gate |
| `code-quality` | flake8 + `black --check` (backend, analytics, QA) → inline-script parse of the frontend HTML → `npm run lint` (ESLint) → `npm run format` (Prettier)                                                            | Lint gate           |

From Day 4 on, the root `pytest -q` also runs the Milestone 1 suite, because `QA/milestone1/tests` was added to `testpaths` in `pyproject.toml`.

### Finding: the workflow has not run on GitHub yet

`git ls-files .github` returns nothing on branch `Team-1`. The workflow and the defect template exist locally but are **untracked**, so no PR has been checked yet. FR-10 is only met once `.github/` is committed and a PR to `develop`/`main` shows both jobs. Logged as part of the Day 7 open items.

Running the same steps locally on 2026-10-02:

| CI step                            | Local result                                             |
| ---------------------------------- | -------------------------------------------------------- |
| Build (`import app.main`)          | OK ("Traffic Vision Backend API")                        |
| `pytest -q` (root)                 | 138 passed, 1 failed (DEF-M1-006), 21 skipped, 5 xfailed |
| Analytics suite                    | 60 passed                                                |
| AI engine suite                    | 19 passed                                                |
| flake8 / black / ESLint / Prettier | Fail (DEF-M1-007, see Day 6)                             |

## 2. Local integration environment: `docker-compose.dev.yml`

`docker compose -f docker-compose.dev.yml config --services` (evidence: `compose_services.txt`):

| Service     | Image / build                       | Port | Health check     | M1 role                       |
| ----------- | ----------------------------------- | ---- | ---------------- | ----------------------------- |
| `postgres`  | `timescale/timescaledb:2.17.2-pg16` | 5432 | `pg_isready`     | Users, roles and traffic data |
| `redis`     | `redis:7-alpine`                    | 6379 | `redis-cli ping` | Live-read cache               |
| `backend`   | backend `Dockerfile` (gateway)      | 8000 | `GET /health`    | Auth, Traffic, Predict        |
| `ai`        | `ai-engine/Dockerfile`              | 8010 | `GET /health`    | Heuristic stub `heuristic-v0` |
| `analytics` | reuses the backend image            | 8001 | `GET /`          | Milestone 3, not tested here  |

- `backend` waits for healthy `postgres` and `redis`. `ai` waits for a healthy `backend` and reads live traffic from `TRAFFIC_API_URL=http://backend:8000/api/v1/traffic/live`.
- Credentials come from `.env.dev`, which is git-ignored. `.env.dev.example` is the template.
- This environment is **for local integration only and is not a deployment target**.

### Bring-up and team check

```bash
cp .env.dev.example .env.dev          # first time only
docker compose -f docker-compose.dev.yml up -d --build
docker ps                              # all M1 services "healthy"
python QA/milestone1/day5/m1_live_stack_check.py
```

Stack status on 2026-10-02 (`day5/day5_stack_status.txt`): postgres, redis, backend and ai were healthy. analytics was unhealthy, but it is a Milestone 3 service and outside M1 scope.

> If you pulled a compose change, run `up -d` again. `docker start` reuses old containers with their old environment, which is what caused DEF-M1-005.
