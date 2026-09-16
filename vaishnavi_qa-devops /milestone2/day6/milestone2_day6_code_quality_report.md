# Day 6 — Code Quality Report (Milestone 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Per SRS Section 10.5 Day 6: "run static code-quality checks on new Milestone 2 code." Run ahead of schedule since the codebase was already available; will be re-run once open defects are fixed to confirm no regressions.

## Tools & scope
- **Black** (`--check`) and **Flake8** — `backend/` and `Data/M2_Day6_Traffic_Monitoring_/`
- **ESLint** and **Prettier** — whole repo, matching `.github/workflows/ci.yml`'s "Run lint and format checks" step exactly

## Config gaps found and fixed first
Both checks were unusable as configured:
- **No `.prettierignore` and no root `.gitignore` existed.** `npm run format` was scanning `.venv/` (tens of thousands of vendored files, including a full copy of `numpy`) before even reaching real project files. **Fixed**: added `.prettierignore` (excludes `.venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `*.db`, `package-lock.json`). A proper root `.gitignore` is still outstanding — see Open Items.

## Backend (`backend/`)

### Black — 22 of 28 files need reformatting
Essentially the entire backend fails formatting. Not spot-checked line by line since the volume is high; recommend the backend intern just run `black backend` locally before their next push.

### Flake8 — 275 violations, but concentrated
```
164  backend/traffic_authentication_complete/app/main.py   ← dead code (unused 3rd auth app, see Day 2 findings)
 31  backend/app/routes/auth.py
 18  backend/app/services/maps_wrapper.py
 13  backend/app/routes/route_analysis.py
  9  backend/app/security/auth.py   ← also dead code (DEF-M2-006)
  ... (rest are 1–5 each across smaller files)
```
**60% of all backend flake8 violations are in a single unused, non-authoritative file** (`traffic_authentication_complete/app/main.py` — the duplicate auth service the user already confirmed is not canonical). Recommend deleting the dead/duplicate files (`app/src/`, `app/security/auth.py`, `traffic_authentication_complete/`) rather than reformatting code nobody runs — that alone removes ~173 of 275 violations for free. Logged as **DEF-M2-011**.

## Data Engineering module (`Data/M2_Day6_Traffic_Monitoring_/`)
Newly discovered this session — Intern 2's actual Milestone 2 data pipeline delivery (see separate integration note below).
- **Black**: 15 of 19 files need reformatting.
- **Flake8**: 31 violations total, none concentrated in dead code — much cleaner ratio than backend.
- **Tests**: all 35 of her own tests pass (`pytest -q` in that folder).

## Frontend (`Front-end (2)/Front-end/api.js`, via `npm run lint`)
**8 errors, 8 warnings:**
- `no-useless-catch` ×2 (`authAPI.login`, `authAPI.register`) — `try { return await X() } catch (err) { throw err; }` does nothing; safe to delete the try/catch.
- `no-unused-vars` ×6 (`authAPI`, `predictAPI`, `routeAPI`, `getCongestionBadgeInfo`, `logout`, `getDashboardUrl`) — **likely false positives**, not real dead code. `api.js` is loaded as a plain `<script>` (not an ES module), and these are consumed as implicit globals from inline `<script>` blocks in the HTML files (`onclick="logout()"`, `authAPI.login(...)` in `Login.html`, etc.) — ESLint can't see across separate HTML files, so it can't trace the usage. Real fix is an ESLint config change (e.g. an `/* exported ... */` comment or a `no-unused-vars` override for globals), not a code change. Logged as **DEF-M2-012** (Low, config-only).
- `no-console` ×8 warnings — intentional fallback-mode logging (`console.warn` when backend is unreachable); not a real issue, but worth deciding whether to keep as warnings or silence via config.

### Prettier — 51 files need formatting
Once properly scoped (see config gap above), 51 files fail formatting — spread across nearly every `.md`, `.yml`, `.json`, and `.html` file in the repo, including config files like `.eslintrc.json` and `ci.yml` themselves. This is expected for a repo that's never run Prettier `--write` — not a specific code defect, just confirms the format gate has never actually been enforced.

## New defects logged
| ID | Description | Severity |
|---|---|---|
| DEF-M2-011 | 60% of backend flake8 violations (164/275) sit in dead/duplicate code (`traffic_authentication_complete/`, `app/security/auth.py`) that should be deleted, not reformatted | Low |
| DEF-M2-012 | ESLint flags 6 real `api.js` exports as unused vars — false positive from cross-file globals, needs an ESLint config fix, not a code fix | Low |
| DEF-M2-013 | `Data/M2_Day6_Traffic_Monitoring_/.env` has a plaintext DB password (`traffic123`), same pattern as `backend/.env` — repo-wide credential hygiene gap, needs a root `.gitignore` | Medium |

## Open items (not done this session)
- Root `.gitignore` still doesn't exist — flagged twice now (Day 2, Day 6) across two different interns' `.env` files. Recommend prioritizing this before the next commit from anyone on the team.
- `npm run format -- --write` / `black backend` / `black Data/M2_Day6_Traffic_Monitoring_` not run — QA doesn't own other interns' code, so formatting fixes are left for each owner to apply and re-verify.
- Full regression pass (official Day 6's other half) still blocked on DEF-M2-002/003/004/007 being fixed.

## Overall Status
Code-quality gate is technically "failing" everywhere right now (Black and Flake8 both red on `backend/`, ESLint red on `api.js`, Prettier red repo-wide) — but the substance is uneven: the frontend's issues are minor/config-level, Intern 2's module is close to clean, and the backend's real issue is dead code inflating the numbers rather than the active code being badly written. Recommend each intern runs `black`, `flake8`, and `npm run lint` locally before their next push once DEF-M2-002–007 are fixed, so the quality gate and the functional fixes land together.
