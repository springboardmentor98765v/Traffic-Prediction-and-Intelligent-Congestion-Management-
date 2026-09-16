# Day 5 — Prioritized Integration Defect Backlog

## 1. Document Control & Metadata

| Item | Details |
|---|---|
| **Project** | TrafficVision AI — Smart Traffic Prediction & Congestion Management System |
| **Milestone** | Milestone 2 — Traffic Prediction & Route Optimization |
| **Activity** | Day 5 Defect Triage & Prioritization for Day 6 Remediation |
| **Custodian** | Intern 5 — QA, DevOps & Release Engineering |
| **Date** | Day 5, Milestone 2 |
| **Target Resolution Window** | Day 6 Regression & Bug-Fixing Sprint |

---

## 2. Prioritization Framework & Triage Summary

Defects identified during the Day 5 full integration test run have been categorized into three priority tiers based on milestone impact:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRIORITY 1: BLOCKERS (P1)                       │
│  Must be merged and verified on Day 6 before regression testing run.   │
│  - DEF-M2-001: Route Analysis Router Mounting on API Gateway           │
│  - DEF-M2-002: Real ML Prediction Model Serving & Missing Endpoints     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                       PRIORITY 2: HIGH IMPACT (P2)                     │
│  Must be resolved prior to Day 7 Final Milestone Sign-off.             │
│  - DEF-M2-003: Congestion-Aware Route Ranking RPC                     │
│  - DEF-M2-004: Historical Traffic API Exposure on Gateway              │
│  - DEF-M2-006: Frontend Route Analysis Page & Report Download Button   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    PRIORITY 3: MEDIUM ENHANCEMENTS (P3)                │
│  Targeted for Day 6/7; non-blocking with documented workarounds.       │
│  - DEF-M2-005: Road Conditions Mutation RBAC Boundary                  │
│  - DEF-M2-008: Road Conditions Hazard Ingestion Schema                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Prioritized Defect Registry

| Rank | Defect ID | Severity | Priority | Affected Service | Summary & Fix Requirement | Owner | Target Day |
|---|---|---|---|---|---|---|---|
| **1** | `DEF-M2-001` | **Critical** | **P1 - Blocker** | API Gateway / Route Analysis | Mount `route.py` on `/api/v1/route` with `/optimize`, `/alternate`, `/travel-time`, and `/conditions`. | Intern 1 | Day 6 (AM) |
| **2** | `DEF-M2-002` | **Critical** | **P1 - Blocker** | AI Prediction Engine | Replace `heuristic-v0` with trained model (`model-v1.0`); implement `/predict/peak-hours` and `/predict/delay`. | Intern 3 | Day 6 (AM) |
| **3** | `DEF-M2-003` | **High** | **P2 - High** | Route Analysis & AI Engine | Wire inter-service RPC so `GET /api/v1/route/alternate` ranks routes by predicted congestion score. | Intern 1 & 3 | Day 6 (PM) |
| **4** | `DEF-M2-006` | **High** | **P2 - High** | Frontend Application | Create `/route-analysis` Leaflet map page; add prediction forecast chart and download report button. | Intern 4 | Day 6 (PM) |
| **5** | `DEF-M2-004` | **High** | **P2 - High** | Historical Data Pipeline | Expose `GET /api/v1/traffic/history` through the Gateway for model feature retrieval. | Intern 2 | Day 6 (PM) |
| **6** | `DEF-M2-005` | **Medium** | **P3 - Medium** | Road Conditions | Connect road hazard query to TimescaleDB road condition status table. | Intern 1 & 2 | Day 7 (AM) |
| **7** | `DEF-M2-008` | **Medium** | **P3 - Medium** | Security / RBAC | Enforce `operator` and `admin` RBAC restriction on `POST /api/v1/route/conditions`. | Intern 1 | Day 7 (AM) |

---

## 4. Remediation Directives for Module Leads

### P1: Route Analysis Gateway Integration (`DEF-M2-001`)
- **Action for Intern 1**:
  - Add router file `Backend/app/routers/route.py`.
  - Register endpoints:
    - `@router.get("/optimize")`
    - `@router.get("/alternate")`
    - `@router.get("/travel-time")`
    - `@router.get("/conditions")`
  - Mount router in `Backend/app/main.py`:
    ```python
    app.include_router(route.router, prefix="/api/v1/route", tags=["Route Analysis"])
    ```
- **Verification Criterion**: Automated test `test_route_analysis.py` returns HTTP 200 OK across all endpoints.

### P1: Real ML Prediction Serving (`DEF-M2-002`)
- **Action for Intern 3**:
  - Update `Sowjanya-ai-ml/src/main.py` and `Backend/app/routers/prediction.py`.
  - Replace heuristic random stub with real model inference returning `"model_version": "model-v1.0"`.
  - Add endpoints:
    - `@router.get("/peak-hours")` returning 24-hour congestion forecast.
    - `@router.get("/delay")` returning delay estimates in minutes.
- **Verification Criterion**: Automated test `test_prediction.py` passes without `"heuristic-v0"` assertion failure.

### P2: Smart Congestion Route Ranking (`DEF-M2-003`)
- **Action for Intern 1 & Intern 3**:
  - When Route Analysis generates candidate geometric paths from OpenStreetMap, iterate over road segments and request predicted congestion from `/api/v1/predict/congestion`.
  - Compute a composite congestion penalty score and sort the returned candidate array in ascending penalty order.
- **Verification Criterion**: `test_route_alternate_ranking` confirms returned routes are ordered by predicted congestion.

### P2: Frontend Route Planning & Report Download (`DEF-M2-006`)
- **Action for Intern 4**:
  - Wire interactive Leaflet map component in `app/route-analysis/page.tsx`.
  - Add Recharts / Chart.js forecast chart in `app/dashboard/page.tsx`.
  - Add "Download Prediction Report" button exporting CSV/PDF summary from `/api/v1/predict/report`.
- **Verification Criterion**: Manual walkthrough of end-to-end user journey renders map polylines and downloads report.

---

## 5. Day 6 Retest & Sign-Off Schedule

```
09:00 - 09:15: Daily Standup — Align on P1 Blocker PRs
09:15 - 12:00: Dev Fix Cycle — Interns 1, 2, 3 land P1/P2 fixes
12:00 - 13:00: QA Retest Cycle 1 — Verify DEF-M2-001 and DEF-M2-002 fixes via automated pytest
13:00 - 15:00: Integration & Frontend Polish — Intern 4 lands UI components
15:00 - 17:00: Full Milestone 1 Regression Pass & Static Code Quality Checks (Black, Flake8, ESLint)
17:00 - 18:00: Daily Wrap-up & Go/No-Go Signal for Day 7 Final Sign-off
```
