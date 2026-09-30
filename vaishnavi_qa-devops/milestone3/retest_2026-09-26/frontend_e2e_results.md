# Milestone 3 Day 5 — Frontend E2E Results (Playwright, Edge)

Executed 2026-09-26 08:33 · frontend served from `front-end/Front-end` at http://127.0.0.1:5500 · `python QA/milestone3/day5/frontend_e2e.py`

**26 pass · 5 fail** (of 31)

| Role     | Check                                                                | Expected                | Actual                                                                                     | Result | Ref        |
| -------- | -------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------ | ------ | ---------- |
| user     | UI login lands on role dashboard                                     | public dashboard.html   | public dashboard.html                                                                      | PASS   |            |
| user     | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                        | PASS   |            |
| user     | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | True                                                                                       | PASS   |            |
| user     | Bell drawer shows detector accident alert (High)                     | False                   | True                                                                                       | FAIL   | DEF-M3-007 |
| user     | Bell drawer shows Critical accident alert                            | False                   | True                                                                                       | FAIL   | DEF-M3-012 |
| user     | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                      | PASS   |            |
| user     | Alerts UI calls GET /alerts/my with its JWT (accepted)               | ≥ 1 call, all 200       | 2 call(s), status ['200']                                                                  | PASS   |            |
| user     | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 2 ok; calls: 127.0.0.1:8001/analytics/trends → 200; 127.0.0.1:8001/analytics/heatmap → 200 | PASS   |            |
| user     | AI recommendations load from AI Insights (:8010)                     | 200                     | FAILED net::ERR_CONNECTION_REFUSED                                                         | FAIL   | DEF-M3-017 |
| user     | Route analysis page reaches /route/* with 200                        | >=1                     | 3                                                                                          | PASS   |            |
| user     | Public user opening admin dashboard is redirected                    | not admin dashboard     | public dashboard.html                                                                      | PASS   |            |
| operator | UI login lands on role dashboard                                     | operator dashboard.html | operator dashboard.html                                                                    | PASS   |            |
| operator | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                        | PASS   |            |
| operator | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | True                                                                                       | PASS   |            |
| operator | Bell drawer shows detector accident alert (High)                     | True                    | True                                                                                       | PASS   |            |
| operator | Bell drawer shows Critical accident alert                            | True                    | True                                                                                       | PASS   |            |
| operator | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                      | PASS   |            |
| operator | Alerts UI calls GET /alerts/my with its JWT (accepted)               | ≥ 1 call, all 200       | 2 call(s), status ['200']                                                                  | PASS   |            |
| operator | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 2 ok; calls: 127.0.0.1:8001/analytics/heatmap → 200; 127.0.0.1:8001/analytics/trends → 200 | PASS   |            |
| operator | AI recommendations load from AI Insights (:8010)                     | 200                     | FAILED net::ERR_CONNECTION_REFUSED                                                         | FAIL   | DEF-M3-017 |
| operator | Route analysis page reaches /route/* with 200                        | >=1                     | 3                                                                                          | PASS   |            |
| admin    | UI login lands on role dashboard                                     | admin dashboard.html    | admin dashboard.html                                                                       | PASS   |            |
| admin    | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                        | PASS   |            |
| admin    | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | True                                                                                       | PASS   |            |
| admin    | Bell drawer shows detector accident alert (High)                     | True                    | True                                                                                       | PASS   |            |
| admin    | Bell drawer shows Critical accident alert                            | True                    | True                                                                                       | PASS   |            |
| admin    | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                      | PASS   |            |
| admin    | Alerts UI calls GET /alerts/my with its JWT (accepted)               | ≥ 1 call, all 200       | 2 call(s), status ['200']                                                                  | PASS   |            |
| admin    | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 2 ok; calls: 127.0.0.1:8001/analytics/heatmap → 200; 127.0.0.1:8001/analytics/trends → 200 | PASS   |            |
| admin    | AI recommendations load from AI Insights (:8010)                     | 200                     | FAILED net::ERR_CONNECTION_REFUSED                                                         | FAIL   | DEF-M3-017 |
| admin    | Route analysis page reaches /route/* with 200                        | >=1                     | 3                                                                                          | PASS   |            |

## Backend calls made by each page

**user · public dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 401
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- console: `error: Failed to load resource: the server responded with a status of 401 (Unauthorized)`
- console: `warning: [AlertsAPI] Could not reach GET /alerts/my – using fallback data. Not authenticated`

**user · Alerts.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**user · analytics.html**

- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8001/analytics/trends` → 200
- `GET 127.0.0.1:8001/analytics/heatmap` → 200
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**user · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → 503
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Failed to load resource: the server responded with a status of 503 (Service Unavailable)`
- console: `warning: ⚠️ Backend route API unavailable, falling back to BFS mock: External maps service (OSRM) is currently unavailable. Please try again later.`

**operator · operator dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 401
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- console: `error: Failed to load resource: the server responded with a status of 401 (Unauthorized)`
- console: `warning: [AlertsAPI] Could not reach GET /alerts/my – using fallback data. Not authenticated`

**operator · Alerts.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**operator · analytics.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8001/analytics/heatmap` → 200
- `GET 127.0.0.1:8001/analytics/trends` → 200
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**operator · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → 503
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Failed to load resource: the server responded with a status of 503 (Service Unavailable)`
- console: `warning: ⚠️ Backend route API unavailable, falling back to BFS mock: External maps service (OSRM) is currently unavailable. Please try again later.`

**admin · admin dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 401
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/predict/peak-hours` → 200
- console: `error: Failed to load resource: the server responded with a status of 401 (Unauthorized)`
- console: `warning: [AlertsAPI] Could not reach GET /alerts/my – using fallback data. Not authenticated`

**admin · Alerts.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**admin · analytics.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8001/analytics/heatmap` → 200
- `GET 127.0.0.1:8001/analytics/trends` → 200
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**admin · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → 503
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Failed to load resource: the server responded with a status of 503 (Service Unavailable)`
- console: `warning: ⚠️ Backend route API unavailable, falling back to BFS mock: External maps service (OSRM) is currently unavailable. Please try again later.`
