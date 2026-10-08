# Milestone 1 Test Summary (for the demo)

**Date:** 2026-10-02 · **Environment:** local Docker Compose plus the in-process pytest suite · **No deployment**

## Numbers

| Suite                                  |  Cases |   Pass | Fail (known defect) |
| -------------------------------------- | -----: | -----: | ------------------: |
| Authentication (TC-AUTH)               |     21 |     18 |                   3 |
| RBAC (TC-RBAC)                         |     13 |     11 |                   2 |
| Traffic Monitoring (TC-TRF)            |      9 |      9 |                   0 |
| Prediction stub (TC-PRED)              |     13 |     13 |                   0 |
| Gateway + frontend (TC-GW, TC-UI)      |     25 |     25 |                   0 |
| **Automated M1 suite**                 | **81** | **76** |               **5** |
| Live stack E2E (TC-INT, with operator) |     13 |     13 |                   0 |
| Browser E2E, M1 checks (3 roles)       |      7 |      7 |                   0 |

Parametrized cases are counted individually, so these counts are higher than the number of IDs in the test-case document.

## Requirement coverage

| FR    | Requirement                              | Result                                                             |
| ----- | ---------------------------------------- | ------------------------------------------------------------------ |
| FR-01 | Register / login → JWT with role         | ✅ (DEF-M1-001: empty password accepted)                           |
| FR-02 | RBAC on protected endpoints              | ⚠️ role-gated routes ✅; monitoring routes are public (DEF-M1-003) |
| FR-03 | Traffic ingestion per road segment       | ✅                                                                 |
| FR-04 | Congestion level per road segment        | ✅                                                                 |
| FR-05 | Live traffic REST APIs                   | ✅                                                                 |
| FR-06 | Heuristic prediction endpoint            | ✅ (`heuristic-v0`; gateway now on `model-v1`)                     |
| FR-07 | Login → role-aware dashboard             | ✅                                                                 |
| FR-08 | Dashboard shows live data and prediction | ✅                                                                 |
| FR-09 | All services in local Docker Compose     | ✅                                                                 |
| FR-10 | CI lint / build / test on every PR       | ❌ workflow not committed; lint gate red                           |
| FR-11 | Documented integration and RBAC cycle    | ✅ this folder                                                     |

## Demo talking points

1. `docker compose -f docker-compose.dev.yml up -d`, then `docker ps` shows all M1 services healthy.
2. `python QA/milestone1/day5/m1_live_stack_check.py` gives 11/11 (13/13 with operator credentials).
3. Log in as Public, Operator and Admin in `Login.html`; each lands on its own dashboard, and Public is bounced from the admin page.
4. The dashboard KPIs equal `GET /api/v1/traffic/density` (live Postgres data).
5. `python -m pytest QA/milestone1/tests` gives 76 passed, and the 5 xfails are each a logged defect.
