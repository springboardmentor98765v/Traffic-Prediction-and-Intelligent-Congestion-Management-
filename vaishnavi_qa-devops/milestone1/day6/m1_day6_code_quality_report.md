# Day 6: Static Code-Quality Report

**Executed:** 2026-10-02 · **Tools:** Flake8 7.3, Black 26.5, ESLint 8, Prettier 3, `QA/tools/check_inline_js.js` (same commands as the CI `code-quality` job)
**Evidence:** `day6_code_quality_output.txt`

## 1. Summary

| Check                   | Scope                         | Result                                               | CI gate |
| ----------------------- | ----------------------------- | ---------------------------------------------------- | ------- |
| Flake8                  | Backend (`Intern_AI AND ML`)  | 230 findings                                         | ❌      |
| Flake8                  | Analytics (`daa/...`)         | 42 findings                                          | ❌      |
| Flake8                  | AI Engine                     | 41 findings (not in the CI scope)                    | n/a     |
| Flake8                  | `QA/`                         | 2 (E501 in `QA/milestone3/day6/regression_m1_m2.py`) | ❌      |
| Flake8                  | `QA/milestone1/` (new)        | **0**                                                | ✅      |
| Black `--check`         | Backend / Analytics / AI / QA | 40 / 25 / 9 / 1 files need reformatting              | ❌      |
| Black `--check`         | `QA/milestone1/` (new)        | **clean**                                            | ✅      |
| Inline `<script>` parse | Frontend HTML (9 pages)       | All inline scripts parse                             | ✅      |
| ESLint                  | Repo JS                       | 93 problems (42 errors, 51 warnings)                 | ❌      |
| Prettier `--check`      | Repo                          | 138 files need formatting                            | ❌      |

**Verdict:** the CI `code-quality` job would **fail** today (DEF-M1-007). The new M1 QA code is clean.

> Measurement note: passing `--exclude` on the command line replaces the `.flake8` exclude list. That pulls the backend's own `.venv` into the scan and reports about 43,000 findings. The numbers above use the repo's `.flake8` config, the same way CI does.

## 2. Findings that are real bugs (fix first)

| Rule                                        | Where                                                                               | Risk                                                                                                                      |
| ------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| E722 ×6                                     | `app/services/traffic_service.py` lines 123, 169, 220, 262, 343, 384                | Bare `except:` swallows every error, including `KeyboardInterrupt`, and hides DB failures behind the sample-data fallback |
| F811                                        | `data/M2_Day7_Traffic_Monitoring_/src/traffic_service.py:579` and the `daa/` copy   | `get_road_condition` is defined twice; the second definition silently wins                                                |
| F841                                        | `historical_data_cleaner.py:37` (both copies)                                       | Unused `timestamp`, possibly an unfinished validation                                                                     |
| ESLint `no-useless-catch` ×6, `no-empty` ×4 | `api.js`: 4 in `Front-end(m-3) (1)`, 4 in `vennela_frontend`, 2 in the backend copy | Empty or rethrow-only `catch` blocks hide frontend errors                                                                 |
| ESLint `no-unused-vars` ×32                 | `api.js` copies, `QA/tools/check_inline_js.js` (2)                                  | Dead code                                                                                                                 |

## 3. Style-only findings (bulk, auto-fixable)

Top Flake8 codes across backend, analytics and AI: E501 line too long (60), W293 whitespace on blank line (55), E302 blank lines (50), W292 no newline at end of file (47), E402 import not at top (28), W291 (17), F401 unused import (13).
Most of these go away with `python -m black <dir>` and `npx prettier --write .`. Each owner should run those on their own folder in a separate formatting-only PR so it doesn't mix with logic changes.

## 4. Other observations

- **The frontend exists in three copies** (`Front-end(m-3) (1)/Front-end`, `vennela_frontend/`, `backend_updated/.../Front-end/`), and they differ. That triples the ESLint and Prettier findings and makes it unclear which copy is tested. CI and these reports use `Front-end(m-3) (1)/Front-end`. Recommendation: keep one copy.
- **The traffic-monitoring code also exists in three copies** (`chinmai_data-engineering/`, `daa/M3_Day6_Traffic_Monitoring_/`, `backend_updated/.../data/M2_Day7_Traffic_Monitoring_/`). The same F811/F841 findings appear in each.
- `.prettierignore` does not exclude the large CSV / SQL / evidence folders, so the 138 count includes generated QA output.

## 5. Actions

| Owner    | Action                                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------- |
| Intern 1 | Replace the bare `except:` blocks in `traffic_service.py`; run black on `app/`                                        |
| Intern 2 | Remove the duplicate `get_road_condition`; black the analytics folder                                                 |
| Intern 3 | Black and flake8 the `ai-engine/`                                                                                     |
| Intern 4 | Fix `no-useless-catch` / `no-empty` in `api.js`; pick one frontend copy                                               |
| Intern 5 | Fix the 2 E501 in `QA/milestone3/day6/regression_m1_m2.py`; add evidence folders to `.prettierignore`; fix DEF-M1-006 |
