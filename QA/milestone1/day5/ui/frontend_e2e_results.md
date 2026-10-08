# Milestone 3 Day 5 — Frontend E2E Results (Playwright, Edge)

Executed 2026-10-02 18:35 · frontend served from `Front-end(m-3) (1)/Front-end` at http://127.0.0.1:5500 · `python QA/milestone3/day5/frontend_e2e.py`

**27 pass · 4 fail** (of 31)

| Role     | Check                                                                | Expected                | Actual                                                                                                                                           | Result | Ref            |
| -------- | -------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------ | -------------- |
| user     | UI login lands on role dashboard                                     | public dashboard.html   | public dashboard.html                                                                                                                            | PASS   |                |
| user     | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                                                                              | PASS   |                |
| user     | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | False                                                                                                                                            | FAIL   | DEF-M3-018     |
| user     | Bell drawer shows detector accident alert (High)                     | False                   | False                                                                                                                                            | PASS   |                |
| user     | Bell drawer shows Critical accident alert                            | False                   | False                                                                                                                                            | PASS   |                |
| user     | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                                                                            | PASS   |                |
| user     | Alerts UI calls GET /alerts/my with its JWT (accepted)               | ≥ 1 call, all 200       | 2 call(s), status ['200']                                                                                                                        | PASS   |                |
| user     | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 0 ok; calls: 127.0.0.1:8001/analytics/trends → FAILED net::ERR_EMPTY_RESPONSE; 127.0.0.1:8001/analytics/heatmap → FAILED net::ERR_EMPTY_RESPONSE | FAIL   | DEF-M3-013/014 |
| user     | AI recommendations load from AI Insights (:8010)                     | 200                     | 200; 404                                                                                                                                         | PASS   |                |
| user     | Route analysis page reaches /route/* with 200                        | >=1                     | 4                                                                                                                                                | PASS   |                |
| user     | Public user opening admin dashboard is redirected                    | not admin dashboard     | public dashboard.html                                                                                                                            | PASS   |                |
| operator | UI login lands on role dashboard                                     | operator dashboard.html | operator dashboard.html                                                                                                                          | PASS   |                |
| operator | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                                                                              | PASS   |                |
| operator | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | True                                                                                                                                             | PASS   |                |
| operator | Bell drawer shows detector accident alert (High)                     | True                    | True                                                                                                                                             | PASS   |                |
| operator | Bell drawer shows Critical accident alert                            | True                    | True                                                                                                                                             | PASS   |                |
| operator | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                                                                            | PASS   |                |
| operator | Alerts UI calls GET /alerts/my with its JWT (accepted)               | ≥ 1 call, all 200       | 2 call(s), status ['200']                                                                                                                        | PASS   |                |
| operator | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 0 ok; calls: 127.0.0.1:8001/analytics/heatmap → FAILED net::ERR_EMPTY_RESPONSE; 127.0.0.1:8001/analytics/trends → FAILED net::ERR_EMPTY_RESPONSE | FAIL   | DEF-M3-013/014 |
| operator | AI recommendations load from AI Insights (:8010)                     | 200                     | 200; 404                                                                                                                                         | PASS   |                |
| operator | Route analysis page reaches /route/* with 200                        | >=1                     | 4                                                                                                                                                | PASS   |                |
| admin    | UI login lands on role dashboard                                     | admin dashboard.html    | admin dashboard.html                                                                                                                             | PASS   |                |
| admin    | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                                                                              | PASS   |                |
| admin    | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | True                                                                                                                                             | PASS   |                |
| admin    | Bell drawer shows detector accident alert (High)                     | True                    | True                                                                                                                                             | PASS   |                |
| admin    | Bell drawer shows Critical accident alert                            | True                    | True                                                                                                                                             | PASS   |                |
| admin    | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                                                                            | PASS   |                |
| admin    | Alerts UI calls GET /alerts/my with its JWT (accepted)               | ≥ 1 call, all 200       | 2 call(s), status ['200']                                                                                                                        | PASS   |                |
| admin    | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 0 ok; calls: 127.0.0.1:8001/analytics/heatmap → FAILED net::ERR_EMPTY_RESPONSE; 127.0.0.1:8001/analytics/trends → FAILED net::ERR_EMPTY_RESPONSE | FAIL   | DEF-M3-013/014 |
| admin    | AI recommendations load from AI Insights (:8010)                     | 200                     | 200; 404                                                                                                                                         | PASS   |                |
| admin    | Route analysis page reaches /route/* with 200                        | >=1                     | 4                                                                                                                                                | PASS   |                |

## Backend calls made by each page

**user · public dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 401
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- console: `error: Failed to load resource: the server responded with a status of 401 (Unauthorized)`
- console: `warning: [AlertsAPI] Could not reach GET /alerts/my – using fallback data. Not authenticated`

**user · Alerts.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 404
- `GET 127.0.0.1:8010/ai/recommendations` → 404
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 200 ×2
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`

**user · analytics.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8001/analytics/trends` → FAILED net::ERR_EMPTY_RESPONSE
- `GET 127.0.0.1:8001/analytics/heatmap` → FAILED net::ERR_EMPTY_RESPONSE
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 404
- `GET 127.0.0.1:8010/ai/recommendations` → 404
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 200 ×2
- console: `error: Failed to load resource: net::ERR_EMPTY_RESPONSE`
- console: `warning: [AnalyticsTrends] Fallback to mock — Failed to fetch`
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`

**user · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → 200
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200

**operator · operator dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 401
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200 ×2
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- `GET 127.0.0.1:8000/api/v1/predict/peak-hours` → 200
- console: `error: Failed to load resource: the server responded with a status of 401 (Unauthorized)`
- console: `warning: [AlertsAPI] Could not reach GET /alerts/my – using fallback data. Not authenticated`

**operator · Alerts.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 404
- `GET 127.0.0.1:8010/ai/recommendations` → 404
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 200 ×2
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`

**operator · analytics.html**

- `GET 127.0.0.1:8001/analytics/heatmap` → FAILED net::ERR_EMPTY_RESPONSE
- `GET 127.0.0.1:8001/analytics/trends` → FAILED net::ERR_EMPTY_RESPONSE
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 404
- `GET 127.0.0.1:8010/ai/recommendations` → 404
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 200 ×2
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- console: `error: Failed to load resource: net::ERR_EMPTY_RESPONSE`
- console: `warning: [AnalyticsTrends] Fallback to mock — Failed to fetch`
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`

**operator · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → 200

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
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 404
- `GET 127.0.0.1:8010/ai/recommendations` → 404
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 200 ×2
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`

**admin · analytics.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8001/analytics/heatmap` → FAILED net::ERR_EMPTY_RESPONSE
- `GET 127.0.0.1:8001/analytics/trends` → FAILED net::ERR_EMPTY_RESPONSE
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 404
- `GET 127.0.0.1:8010/ai/recommendations` → 404
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → 200 ×2
- console: `error: Failed to load resource: net::ERR_EMPTY_RESPONSE`
- console: `warning: [AnalyticsTrends] Fallback to mock — Failed to fetch`
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`

**admin · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → 200
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
