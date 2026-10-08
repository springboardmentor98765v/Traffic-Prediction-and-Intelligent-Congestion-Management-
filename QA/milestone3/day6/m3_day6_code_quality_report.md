# Milestone 3 — Day 6 Code-Quality Report (Intern 5)

Date: 2026-09-25 · Tools (same as CI): flake8 + black (`pyproject.toml`: line length 100), ESLint 8
(`.eslintrc.json`), Prettier 3, plus a new inline-script syntax check for HTML pages
(`QA/tools/check_inline_js.js`)

## Verdict: ⚠️ No logic bugs in the new M3 Python code, but 1 critical syntax error in the frontend

- **New M3 Python code (17 files):** 48 flake8 findings, all cosmetic (whitespace, blank lines,
  line length). The only pyflakes hit is intentional. 16 of 17 files need `black`.
- **Frontend:** 1 **syntax error** that breaks the operator dashboard (DEF-M3-023, High).
  `api.js` has 4 real lint errors, all minor.
- **Tests:** Data has a strong suite (49 passing). The Alert Service and AI detector have **no unit
  tests from their owners** (only QA's tests cover them).
- **QA-owned code and config:** cleaned to 0 flake8 / 0 black / 0 prettier issues. The ESLint
  false positive DEF-M2-012 is closed.

## Checkpoints (SRS Day 6)

- [x] **Static code-quality checks run on new M3 code:** per file and per owner, below.
- [x] **Support interns closing out integration bugs:** every finding below names its file, line
      and fix, and the fix lists were sent to each intern.

## 1. New Milestone 3 Python code

| File                                       | Owner    | flake8 | black           | Notes                                                                                                                    |
| ------------------------------------------ | -------- | ------ | --------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `backend (1)/…/app/routes/alerts.py`       | Intern 1 | 15     | reformat        | whitespace, blank lines; no logic findings (RBAC gap is DEF-M3-005, not a lint issue)                                    |
| `…/app/models/alert.py`                    | Intern 1 | 2      | reformat        |                                                                                                                          |
| `…/app/main.py`                            | Intern 1 | 4      | reformat        | F401 `app.models.alert` unused: **false positive**, the import registers the model for `create_all` (add `# noqa: F401`) |
| `…/automate_accident_alerts.py`            | Intern 3 | 9      | reformat        |                                                                                                                          |
| `…/anomaly_detector.py`                    | Intern 3 | 1      | reformat        |                                                                                                                          |
| `…/m3_day2_congestion_watcher.py`          | Intern 2 | 1      | reformat        | **identical copy** also in `Data/src/`: keep one                                                                         |
| `Data/src/main.py`                         | Intern 2 | 7      | reformat        | E402 imports after code                                                                                                  |
| `Data/src/analytics_service.py`            | Intern 2 | 1      | reformat        |                                                                                                                          |
| `Data/src/analytics_cache.py`              | Intern 2 | 0      | reformat        | Redis client has no timeouts: DEF-M3-020 (found by testing, not lint)                                                    |
| `Data/src/heatmap_service.py`              | Intern 2 | 1      | reformat        |                                                                                                                          |
| `Data/src/report_service.py`               | Intern 2 | 0      | reformat        |                                                                                                                          |
| `Data/src/m3_day2_congestion_watcher.py`   | Intern 2 | 1      | reformat        | duplicate (see above)                                                                                                    |
| `Data/src/verify_analytics_performance.py` | Intern 2 | 0      | reformat        |                                                                                                                          |
| `Data/tests/test_m3_*.py` (4 files)        | Intern 2 | 6      | 3 of 4 reformat |                                                                                                                          |
| **Total (17 files)**                       |          | **48** | **16 / 17**     |                                                                                                                          |

**flake8 findings by type:** E302/E305/E303 blank lines 14 · W293/W291 trailing whitespace 15 ·
W292 missing final newline 11 · E402 import position 4 · E501 long lines 3 · F401 1 (false
positive). **No undefined names, unused variables, or other pyflakes logic findings.**

**Fix for every owner:** `python -m black <your files>` then `python -m flake8 <your files>`.
About 44 of the 48 findings disappear with black alone.

## 2. Frontend (Intern 4)

| Check                                              | Result                                       | Details                                                                                                                                                                                                                                                                    |
| -------------------------------------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Inline-script syntax (new check)                   | ❌ **1 failure**                             | `operator dashboard.html` script #3 (line 535): `Unexpected end of input`. Missing `}` at line 583 disables the whole dashboard (**DEF-M3-023, High**, see regression report). The other 7 pages parse                                                                     |
| ESLint `api.js`                                    | 4 errors, 15 warnings                        | real: `alternateEndpoint` unused param (l.304), 2× `no-useless-catch` (l.386, 403), `time_bucket` unused (l.1733: the synthetic heatmap fallback ignores hour/day and invents road R007, same root as DEF-M3-013). Warnings: `no-console` in fallback logging (acceptable) |
| ESLint stale copy `backend (1)/…/Front-end/api.js` | 5 errors                                     | old duplicate of the frontend inside the backend folder. Delete it (the frontend lives in `Front end/`)                                                                                                                                                                    |
| Prettier                                           | 9 of 9 frontend files need formatting        | `npx prettier --write "Front end"`                                                                                                                                                                                                                                         |
| Size / structure                                   | `api.js` 2,490 lines; `analytics.html` 1,768 | large single files mixing API client, mock data and UI state. Consider splitting mock data out so fallbacks can be switched off in production (Deployment Checklist 7.2)                                                                                                   |

**DEF-M2-012 closed (lint config, QA-owned).** ESLint treated `api.js` as an ES module with
`env.node`, so functions shared with the HTML pages looked unused (10 false errors). An
`.eslintrc.json` override for browser scripts brought `api.js` from 12 errors to 4, and all 4
are real.

## 3. Test coverage of new M3 code

| Module                                              | Owner tests                        | QA tests                              | Assessment                                                                                   |
| --------------------------------------------------- | ---------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------- |
| Analytics service (trends, heatmap, reports, cache) | ✅ 49 passing (11 files, 4 for M3) | 17 cases                              | Good. Tests read `sql/`/`src/` by relative path, so they must run from `Data/` (CI now does) |
| Congestion watcher                                  | ✅ (`test_m3_day2_…`)              | 10 unit + E2E replay                  | Good                                                                                         |
| Alert Service (`alerts.py`)                         | ❌ none                            | 15 API cases, 5 RBAC xfails           | **Gap.** SRS Day 6 asks Intern 1 for tests with fixes                                        |
| Anomaly detector / recommendations                  | ❌ none                            | 3 unit (TC-AL-08a–c) + E2E            | **Gap.** SRS Day 6 asks Intern 3 for unit tests of both                                      |
| Frontend                                            | ❌ none                            | Playwright E2E (3 roles) + regression | Only QA's browser tests                                                                      |

## 4. Whole-repo baseline (what CI's `code-quality` job sees)

| Area                                                                  | flake8                                                                                                                                                | black (files)  | ESLint                        | Prettier (files) |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ----------------------------- | ---------------- |
| Backend folder                                                        | 386 = live `app/` 167 + root scripts 23 + tests 2 + **dead code 199** (`traffic_authentication_complete/` 164, `data/M2_Day7…` copy 30, `app/src/` 5) | 43             | stale `api.js` copy: 5 errors | 25               |
| `Data/`                                                               | 42                                                                                                                                                    | 24             | –                             | 20               |
| `Front end/`                                                          | –                                                                                                                                                     | –              | 4 errors / 15 warnings        | 9                |
| `QA/`, CI, lint config, `docs/`, compose (QA-owned)                   | **0** (was 12)                                                                                                                                        | **0** (was 12) | 0 errors                      | **0** (was 46)   |
| Other copies (`AIML/`, `TrafficVision-AI 3/`, `vaishnavi_qa-devops/`) | –                                                                                                                                                     | –              | –                             | 14               |
| **Total**                                                             | 428                                                                                                                                                   | 67             | 9 errors                      | 74 (was 124)     |

**52% of backend flake8 findings (199 / 386) are in dead or duplicated code.** Deleting it
(DEF-M2-011 + the duplicate folders in Deployment Checklist 1.1) is cheaper than reformatting it.

## 5. QA changes made today (QA-owned files only)

| Change                                                                                                           | Why                                                                     |
| ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `black` + fixes on `QA/`, `tests/`, root `conftest.py`, `tests/test_route_analysis.py`                           | QA code now passes flake8/black; tests still 50 passed, 0 failed        |
| `prettier --write` on `QA/`, `docs/`, `.github/`, `.eslintrc.json`, `.prettierrc.json`, `docker-compose.dev.yml` | Prettier 124 → 74 files; compose and CI YAML re-validated               |
| `.eslintrc.json` override for browser scripts                                                                    | closes DEF-M2-012                                                       |
| New `QA/tools/check_inline_js.js` + CI step                                                                      | ESLint never reads HTML; this would have caught DEF-M3-023 before merge |
| CI: new step runs Intern 2's suite from `Data/`                                                                  | their 49 tests weren't run by CI at all                                 |

Other interns' code was **not** reformatted. Each owner applies black/prettier to their own files.

## 6. Actions per owner

| Owner                              | Action                                                                                                                                                                                                 |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Intern 4 (Frontend)**            | **Fix DEF-M3-023 first** (1 character). Then fix the 4 ESLint errors in `api.js` and run `npx prettier --write "Front end"`                                                                            |
| **Intern 1 (Backend / Team Lead)** | `black` + `flake8` on `app/`, add `# noqa: F401` in `main.py`, write unit tests for `alerts.py`, delete dead code (`traffic_authentication_complete/`, `app/src/`, `Front-end/` copy, `data/M2_Day7…`) |
| **Intern 2 (Data)**                | `black` + `flake8` on `Data/`, keep one copy of the congestion watcher                                                                                                                                 |
| **Intern 3 (AI)**                  | `black` on `anomaly_detector.py` / `automate_accident_alerts.py`; unit tests for the detector and recommendations                                                                                      |

## Reproduce

```
python -m flake8 "backend (1)/backend/Intern_AI AND ML" Data QA
python -m black --check "backend (1)/backend/Intern_AI AND ML" Data QA
npx eslint . --ext .js
npx prettier --check .
node QA/tools/check_inline_js.js "Front end/Front-end"/*.html
cd Data && python -m pytest -q tests
```
