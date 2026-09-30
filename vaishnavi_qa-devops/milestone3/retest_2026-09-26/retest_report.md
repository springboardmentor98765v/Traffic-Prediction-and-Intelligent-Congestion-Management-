# Full Retest — Data, Frontend and Backend updates (2026-09-26)

Tested by: Intern 5 (QA) · Stack: `docker-compose.dev.yml` recreated on the new folders ·
Browser: Edge 153 (Playwright)

## Verdict: 7 defects fixed ✅ · 2 new High bugs ❌ · still not ready for sign-off

The fixes to Analytics, the route fallback and the Alert Service's login requirement are solid.
But the security change to the Alert Service caused two new High bugs:

1. **Public users now see Critical alerts** (DEF-M3-024).
2. **Automatic alerts have stopped completely.** The congestion watcher and the accident script
   are rejected with 401 (DEF-M3-025).

The operator dashboard is still broken (DEF-M3-023, second failed retest).

## 1. What changed in the repo (and what QA had to adapt)

| Change                                                                                      | Effect                                                           | QA action                                                                                                                          |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `backend (1)/` → **`backend/`**                                                             | Running containers pointed at a path that no longer existed      | Updated compose, CI, root `conftest.py`, `pyproject.toml`, ESLint override, QA scripts, `.env.dev.example`; recreated the stack    |
| `Data/` → **`Data/M3_Day5_Traffic_Monitoring_/`**                                           | Analytics container, CI and data setup pointed at the old folder | Updated `ANALYTICS_DIR` in compose + CI, `analytics_setup.sh`                                                                      |
| `.env.dev` gained `JWT_SECRET_KEY`, `ALERT_SERVICE_KEY`                                     | Intended for DEF-M3-021 / producer auth                          | Tested; neither is used by the API (see DEF-M3-021, 025)                                                                           |
| `QA/milestone3/qa_auth.py` **missing** (6 QA scripts import it)                             | QA scripts crashed on import                                     | Rebuilt it from its compiled copy (same functions and `X-Alert-Service-Key` header)                                                |
| Backend folder replaced → `tests/test_route_analysis.py` reverted to the old broken version | DEF-M3-002 came back (401)                                       | Re-applied the QA fix (3/3 backend tests pass)                                                                                     |
| Alert API now needs a JWT                                                                   | QA alert tests created alerts without auth                       | `test_alerts_api.py`, `integration_cycle.py`, `frontend_e2e.py` updated to the secured contract; producers still tested as shipped |

## 2. Results

| Suite                                 | Before (Day 7 / frontend retest) | Now                                | Notes                                                                                 |
| ------------------------------------- | -------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------- |
| `pytest -q` (M1/M2 + backend + QA M3) | 50 passed, 11 xfailed            | **61 passed, 0 failed, 6 xfailed** | each xfail = one open defect (024 ×2, 005 ×2, 025, 016)                               |
| Intern 2's own tests                  | 49 passed                        | **59 passed**                      | new `test_m3_day6_qa_fixes.py`                                                        |
| Integration cycle (API)               | 32 / 44                          | **36 / 46** (2 blocked: AI)        | fails: 016, 025 ×2, 024, 007, 005 ×3                                                  |
| Frontend E2E (3 roles, Edge)          | 18 / 31                          | **26 / 31**                        | fails: public user sees High + Critical accident alerts (007, 024), AI panel ×3 (017) |
| M1/M2 regression                      | 46 / 53                          | **47 / 53**                        | fails: 022 ×4, 023 ×2                                                                 |
| Inline-script syntax                  | 1 fail                           | **1 fail**                         | operator dashboard (023)                                                              |
| Analytics performance                 | ✅                               | ✅ cold ≤ 0.4 s                    |                                                                                       |
| Redis down                            | ❌                               | ❌ trends/heatmap no answer in 5 s | 020                                                                                   |
| Alert delivery script / smoke test    | –                                | ⚠️ could not run fully             | they post with the producer service key, which is rejected (025)                      |

## 3. Defect status after this retest

### Fixed and closed (7)

| Defect                                         | Evidence                                                          |
| ---------------------------------------------- | ----------------------------------------------------------------- |
| DEF-M3-004 `/route/alternate` 500              | now 503 with a message when the maps API is down (agreed fix)     |
| DEF-M3-009 malformed date → 500                | 4xx on trends/heatmap/reports; tests promoted                     |
| DEF-M3-010 report days UTC vs IST              | report day matches trends day; test promoted                      |
| DEF-M3-011 unknown road / inverted range       | 404 / 4xx; tests promoted                                         |
| DEF-M3-012 operators/admins never saw Critical | role now from the JWT; operator + admin see Critical (API and UI) |
| DEF-M3-013 frontend Analytics URLs             | **Analytics page now shows live data for all 3 roles**            |
| DEF-M3-014 Analytics CORS                      | `Access-Control-Allow-Origin` present; browser calls return 200   |

### Partly fixed (still open)

| Defect                             | Fixed                                                  | Still wrong                                                                                         |
| ---------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| DEF-M3-005 alert endpoint security | all endpoints need a JWT                               | any logged-in user, incl. public, can **create alerts (even Critical)** and **mark any alert read** |
| DEF-M3-008 severity vocabulary     | API rejects anything but Low/Medium/High/Critical      | the watcher still sends "Severe"                                                                    |
| DEF-M2-011 dead code               | `traffic_authentication_complete/`, `app/src/` deleted | stale `Front-end/` copy, `data/M2_Day7…` copy, dead `app/security/auth.py` (undefined name `token`) |

### New High defects

| Defect         | What happens                                                                                                                                                                                          | Fix                                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **DEF-M3-024** | **Public users see Critical alerts.** The login token now says `role: "PUBLIC"`, but `alerts.py` hides Critical only when `role == "user"`                                                            | treat `PUBLIC`/`user` the same; better: hide Critical unless the role is operator/admin                |
| **DEF-M3-025** | **No automatic alerts are created.** Congestion watcher and `automate_accident_alerts.py` → 401. `ALERT_SERVICE_KEY` is configured but the API never checks it. 672 real readings → 0 alerts (was 30) | accept `X-Alert-Service-Key` on POST for producers; send it from both producers; map Severe → Critical |

### Not fixed (unchanged)

| Defect                                                                                                 | Owner                   |
| ------------------------------------------------------------------------------------------------------ | ----------------------- |
| **DEF-M3-023** operator dashboard missing `}` (~line 597), 2nd failed retest                           | Intern 4                |
| **DEF-M3-021** JWT secret still hard-coded (`config.py`, `jwt.py`); the new `JWT_SECRET_KEY` is unused | Intern 1                |
| **DEF-M3-017** no AI Insights service on :8010                                                         | Intern 3 / Team Lead    |
| DEF-M3-022 history/aggregate filters ignored                                                           | Intern 2 / backend      |
| DEF-M3-020 Analytics hangs when Redis is down (no client timeouts)                                     | Intern 2                |
| DEF-M3-007 accident alerts (High) visible to public users                                              | Intern 1 + 3 (decision) |
| DEF-M3-016 `created_at` returned without timezone                                                      | Intern 1                |
| DEF-M2-008 scikit-learn not pinned                                                                     | AI / backend            |

**Totals:** 14 open (6 High, 3 Medium, 5 Low), down from 18. 7 closed in this retest.

## 4. Code quality on the new code

- Backend flake8 **386 → 222** (dead code removed). Data 41. QA 0.
- pyflakes: `app/security/auth.py` has an **undefined name `token`** (dead module, part of
  DEF-M2-011). `Data/.../src/traffic_service.py` **defines `get_road_condition` twice** (the
  second silently replaces the first). `historical_data_cleaner.py`: unused variable and an
  f-string without placeholders.
- ESLint: `front-end/.../api.js` 6 errors (unchanged from the frontend retest).

## 5. Reproduce

```
docker compose -f docker-compose.dev.yml up -d
export M3_OUT_DIR=QA/milestone3/retest_2026-09-26
python -m pytest -q -rxX
python QA/milestone3/day5/integration_cycle.py
python QA/milestone3/day5/frontend_e2e.py
python QA/milestone3/day6/regression_m1_m2.py
python QA/milestone3/day6/analytics_perf_cache_check.py
node QA/tools/check_inline_js.js front-end/Front-end/*.html
(cd Data/M3_Day5_Traffic_Monitoring_ && python -m pytest -q tests)
```
