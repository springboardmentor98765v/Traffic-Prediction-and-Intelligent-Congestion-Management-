# Day 3 — CI & Docker Integration Validation (Milestone 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering

## Scope

DEF-M2-002 through DEF-M2-007 (logged on Day 2) are still open — the backend and frontend interns haven't pushed fixes yet, so Day 3 couldn't be a retest pass. Instead it focused on validating the CI/Docker pipeline against the now-structurally-correct `backend/` folder, and looking for anything else blocking a clean pipeline once the open defects are fixed.

## 1. Docker image build — Pass

```
docker compose build backend
```
Builds successfully (`Built` — all 6 layers, cached where unchanged). This was completely blocked on Day 1/2 (no `backend/` folder existed at all); it now works because the folder was flattened to `backend/app/...` matching `docker-compose.yml`'s `build.context: ./backend`.

## 2. Pre-existing stale dev container — informational finding, not touched

Found a separate, already-running container stack on this machine: `trafficvision-backend-dev`, `trafficvision-postgres-dev`, `trafficvision-redis-dev` (up ~11 days, likely from `docker-compose.dev.yml`). It occupies ports 8000/5432/6379, and its logs show it's been **crash-looping**:
```
ModuleNotFoundError: No module named 'joblib'
FileNotFoundError: [Errno 2] No such file or directory: '/app/app/routes'
```
Its image (`backend-backend`, built 11 days ago) is stale relative to current `backend/requirements.txt` and folder layout. Left untouched since it may be another teammate's environment — flagging here rather than restarting it. Recommend whoever owns it either rebuilds it (`docker compose -f docker-compose.dev.yml up --build`) or stops it if abandoned, since a dead container occupying these ports will block anyone else's local Docker testing (including today's — had to test the fresh build on an alternate port, `18000`, to avoid the conflict).

## 3. CI bug found & fixed: missing `PYTHONPATH` for backend import

`backend/app/main.py` (and everything under `backend/app/`) uses absolute imports like `from app.database import engine`, written assuming `backend/` itself is on `sys.path` — correct for the Docker `WORKDIR /app` setup, but not for a plain `python -c` invocation from the repo root.

`.github/workflows/ci.yml`'s **"Verify backend import"** step ran exactly that:
```
python -c "import backend.app.main; print(backend.app.main.app.title)"
```
Reproduced locally — failed before the fix:
```
ModuleNotFoundError: No module named 'app'
```
**Fixed**: added `PYTHONPATH: backend` to both the "Run automated tests" and "Verify backend import" steps in `.github/workflows/ci.yml`. Re-verified locally with the same env var — now prints `TrafficVision AI API` (the app title) successfully. This is the CI-equivalent of the `conftest.py` fix already in place for local pytest runs (that only covers pytest; this covers the separate `python -c` CI step, which conftest.py doesn't touch).

## 4. CI blind spot found & fixed: backend's own tests were never running

`pyproject.toml` had `testpaths = ["tests"]`, which restricts pytest discovery to the root `tests/` folder only. The backend intern shipped their own tests at `backend/tests/test_main.py` and `backend/tests/test_route_analysis.py` — **neither has ever run in CI**, silently.

Ran them directly to check: `test_main.py::test_health_check` passes; `test_route_analysis.py::test_optimize_route` **fails** — and it fails for exactly the reason already tracked as **DEF-M2-004** (route double-prefix), giving independent confirmation of that defect from the backend intern's own test.

**Fixed**: `pyproject.toml` → `testpaths = ["tests", "backend/tests"]`.

### Full suite after both fixes
```
PYTHONPATH=backend pytest -q
```
```
FAILED tests/test_day4_api.py::test_auth_register_login_me_refresh_and_rbac   (DEF-M2-002)
FAILED tests/test_day4_api.py::test_traffic_endpoints                         (DEF-M2-003)
FAILED backend/tests/test_route_analysis.py::test_optimize_route              (DEF-M2-004)
3 failed, 1 passed
```
This is the correct current state — CI should be red right now, because DEF-M2-002/003/004 are genuinely open. Before today's fixes, CI was silently green on the backend-import step (it never actually ran) and blind to 1 of the 3 real failures (backend/tests wasn't discovered at all). Now CI accurately reflects reality, and will naturally go green again once those three defects are fixed — no further CI changes needed.

## 5. New minor defect: unpinned `scikit-learn`

`backend/requirements.txt` lists `scikit-learn` with no version pin. Every test run emits:
```
InconsistentVersionWarning: Trying to unpickle estimator ... from version 1.9.0 when using version 1.9.1.
```
The model file (`backend/ai-engine/models/model-v1.joblib`) was pickled with scikit-learn 1.9.0; the environment installs whatever is latest (1.9.1 here) since nothing pins it. Currently just a warning, not a failure, but an unpinned ML dependency is a real reproducibility/deployment risk — a future `pip install` could land a version with breaking changes to the pickle format. Logged as **DEF-M2-008** (Low) — recommend pinning `scikit-learn==1.9.0` (or re-exporting the model under the newer version) in `backend/requirements.txt`.

## Defects touched today

| ID | Status change |
|---|---|
| DEF-M2-004 | Open → independently reconfirmed via `backend/tests/test_route_analysis.py` |
| DEF-M2-008 (new) | Open — unpinned scikit-learn version, Low severity |
| DEF-M2-009 (new) | **Fixed** — CI `testpaths` blind spot, backend tests now wired in |
| DEF-M2-010 (new) | **Fixed** — CI "Verify backend import" step was silently broken, missing `PYTHONPATH` |

## Overall Status

Day 3 is complete. No new blockers on the DevOps side — the backend Docker image builds cleanly, and CI is now correctly configured to both import the backend and run all of its tests (previously it silently did neither, in two different ways). CI will stay red until DEF-M2-002/003/004 are fixed by the backend intern (expected — see Day 2 report), at which point `docker compose up`, `pytest`, and the GitHub Actions pipeline should all go green together. Nothing further is blocked on the QA/DevOps side; the ball is with the backend intern for 002–004 and 008, and the frontend intern for DEF-M2-007.
