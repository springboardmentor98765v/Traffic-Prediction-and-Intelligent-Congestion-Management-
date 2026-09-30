# Milestone 3 Day 5 — Frontend E2E Results (Playwright, Edge)

Executed 2026-09-25 10:43 · frontend served from `Front end/Front-end` at http://127.0.0.1:5500 · `python QA/milestone3/day5/frontend_e2e.py`

**17 pass · 14 fail** (of 31)

| Role     | Check                                                                | Expected                | Actual                                                                                                                                                                                               | Result | Ref            |
| -------- | -------------------------------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | -------------- |
| user     | UI login lands on role dashboard                                     | public dashboard.html   | public dashboard.html                                                                                                                                                                                | PASS   |                |
| user     | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                                                                                                                                  | PASS   |                |
| user     | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | False                                                                                                                                                                                                | FAIL   | DEF-M3-018     |
| user     | Bell drawer shows detector accident alert (High)                     | False                   | True                                                                                                                                                                                                 | FAIL   | DEF-M3-007     |
| user     | Bell drawer shows Critical accident alert                            | False                   | False                                                                                                                                                                                                | PASS   |                |
| user     | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                                                                                                                                | PASS   |                |
| user     | Alerts UI calls GET /alerts/my with the user's role                  | role sent               | 1 call(s), role NOT sent                                                                                                                                                                             | PASS   |                |
| user     | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 0 ok; calls: 127.0.0.1:8000/analytics/heatmap → 404; 192.168.1.4:8000/analytics/heatmap → FAILED net::ERR_ABORTED; 192.168.1.4:8000/analytics/trends → FAILED net::ERR_ABORTED                       | FAIL   | DEF-M3-013/014 |
| user     | AI recommendations load from AI Insights (:8010)                     | 200                     | FAILED net::ERR_ABORTED; FAILED net::ERR_CONNECTION_REFUSED                                                                                                                                          | FAIL   | DEF-M3-017     |
| user     | Route analysis page reaches /route/* with 200                        | >=1                     | 3                                                                                                                                                                                                    | PASS   |                |
| user     | Public user opening admin dashboard is redirected                    | not admin dashboard     | public dashboard.html                                                                                                                                                                                | PASS   |                |
| operator | UI login lands on role dashboard                                     | operator dashboard.html | operator dashboard.html                                                                                                                                                                              | PASS   |                |
| operator | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                                                                                                                                  | PASS   |                |
| operator | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | False                                                                                                                                                                                                | FAIL   | DEF-M3-018     |
| operator | Bell drawer shows detector accident alert (High)                     | True                    | True                                                                                                                                                                                                 | PASS   |                |
| operator | Bell drawer shows Critical accident alert                            | True                    | False                                                                                                                                                                                                | FAIL   | DEF-M3-012     |
| operator | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                                                                                                                                | PASS   |                |
| operator | Alerts UI calls GET /alerts/my with the user's role                  | role sent               | 1 call(s), role NOT sent                                                                                                                                                                             | FAIL   | DEF-M3-012     |
| operator | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 0 ok; calls: 127.0.0.1:8000/analytics/heatmap → 404; 192.168.1.4:8000/analytics/heatmap → FAILED net::ERR_ABORTED; 192.168.1.4:8000/analytics/trends → FAILED net::ERR_ABORTED                       | FAIL   | DEF-M3-013/014 |
| operator | AI recommendations load from AI Insights (:8010)                     | 200                     | FAILED net::ERR_ABORTED; FAILED net::ERR_CONNECTION_REFUSED                                                                                                                                          | FAIL   | DEF-M3-017     |
| operator | Route analysis page reaches /route/* with 200                        | >=1                     | 3                                                                                                                                                                                                    | PASS   |                |
| admin    | UI login lands on role dashboard                                     | admin dashboard.html    | admin dashboard.html                                                                                                                                                                                 | PASS   |                |
| admin    | Session holds a real JWT (not mock-dev-token)                        | JWT                     | JWT                                                                                                                                                                                                  | PASS   |                |
| admin    | Alerts page list shows the Alert Service accident alert (R004, High) | True                    | False                                                                                                                                                                                                | FAIL   | DEF-M3-018     |
| admin    | Bell drawer shows detector accident alert (High)                     | True                    | True                                                                                                                                                                                                 | PASS   |                |
| admin    | Bell drawer shows Critical accident alert                            | True                    | False                                                                                                                                                                                                | FAIL   | DEF-M3-012     |
| admin    | Bell drawer is live data, not seeded mock notifications              | False                   | False                                                                                                                                                                                                | PASS   |                |
| admin    | Alerts UI calls GET /alerts/my with the user's role                  | role sent               | 1 call(s), role NOT sent                                                                                                                                                                             | FAIL   | DEF-M3-012     |
| admin    | Analytics page loads live data from Analytics service (:8001)        | >=1 call with 200       | 0 ok; calls: 127.0.0.1:8000/analytics/heatmap → 404; 192.168.1.4:8000/analytics/trends → FAILED net::ERR_CONNECTION_REFUSED; 192.168.1.4:8000/analytics/heatmap → FAILED net::ERR_CONNECTION_REFUSED | FAIL   | DEF-M3-013/014 |
| admin    | AI recommendations load from AI Insights (:8010)                     | 200                     | FAILED net::ERR_CONNECTION_REFUSED                                                                                                                                                                   | FAIL   | DEF-M3-017     |
| admin    | Route analysis page reaches /route/* with 200                        | >=1                     | 3                                                                                                                                                                                                    | PASS   |                |

## Backend calls made by each page

**user · public dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200

**user · Alerts.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 192.168.1.4:8010/api/v1/ai/recommendations` → FAILED net::ERR_ABORTED ×3
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**user · analytics.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/analytics/heatmap` → 404
- `GET 192.168.1.4:8010/api/v1/ai/recommendations` → FAILED net::ERR_ABORTED ×3
- `GET 192.168.1.4:8000/analytics/heatmap` → FAILED net::ERR_ABORTED
- `GET 192.168.1.4:8000/analytics/trends` → FAILED net::ERR_ABORTED
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`
- console: `warning: [AnalyticsTrends] Fallback to mock — signal timed out`

**user · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → FAILED net::ERR_FAILED
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Access to fetch at 'http://127.0.0.1:8000/api/v1/route/alternate?origin=12.975,77.585&destination=12.935,77.625' from origin 'http://127.0.0.1:5500' has been blocked by CORS`
- console: `error: Failed to load resource: net::ERR_FAILED`
- console: `warning: ⚠️ Backend route API unavailable, falling back to BFS mock: Failed to fetch`

**operator · operator dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200

**operator · Alerts.html**

- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- `GET 192.168.1.4:8010/api/v1/ai/recommendations` → FAILED net::ERR_ABORTED ×3
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**operator · analytics.html**

- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/analytics/heatmap` → 404
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 192.168.1.4:8010/api/v1/ai/recommendations` → FAILED net::ERR_ABORTED ×3
- `GET 192.168.1.4:8000/analytics/heatmap` → FAILED net::ERR_ABORTED
- `GET 192.168.1.4:8000/analytics/trends` → FAILED net::ERR_ABORTED
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`
- console: `warning: [AnalyticsTrends] Fallback to mock — signal timed out`

**operator · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → FAILED net::ERR_FAILED
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Access to fetch at 'http://127.0.0.1:8000/api/v1/route/alternate?origin=12.975,77.585&destination=12.935,77.625' from origin 'http://127.0.0.1:5500' has been blocked by CORS`
- console: `error: Failed to load resource: net::ERR_FAILED`
- console: `warning: ⚠️ Backend route API unavailable, falling back to BFS mock: Failed to fetch`

**admin · admin dashboard.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200 ×2
- `POST 127.0.0.1:8000/api/v1/auth/login` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/predict/peak-hours` → 200

**admin · Alerts.html**

- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/density` → 200
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 192.168.1.4:8010/api/v1/ai/recommendations` → FAILED net::ERR_ABORTED ×3
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`

**admin · analytics.html**

- `GET 127.0.0.1:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8010/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- `GET 127.0.0.1:8000/analytics/heatmap` → 404
- `GET 192.168.1.4:8000/analytics/trends` → FAILED net::ERR_CONNECTION_REFUSED
- `GET 192.168.1.4:8000/analytics/heatmap` → FAILED net::ERR_CONNECTION_REFUSED
- `GET 192.168.1.4:8010/api/v1/ai/recommendations` → FAILED net::ERR_CONNECTION_REFUSED ×3
- console: `error: Failed to load resource: net::ERR_CONNECTION_REFUSED`
- console: `error: Failed to load resource: the server responded with a status of 404 (Not Found)`
- console: `warning: [AnalyticsTrends] Fallback to mock — Failed to fetch`

**admin · route-analysis.html**

- `GET 127.0.0.1:8000/api/v1/alerts/my` → 200
- `GET 127.0.0.1:8000/api/v1/route/conditions` → 200
- `GET 127.0.0.1:8000/api/v1/route/alternate` → FAILED net::ERR_FAILED
- `GET 127.0.0.1:8000/api/v1/route/optimize` → 200
- `GET 127.0.0.1:8000/api/v1/route/travel-time` → 200
- `GET 127.0.0.1:8000/api/v1/traffic/live` → 200
- console: `error: Access to fetch at 'http://127.0.0.1:8000/api/v1/route/alternate?origin=12.975,77.585&destination=12.935,77.625' from origin 'http://127.0.0.1:5500' has been blocked by CORS`
- console: `error: Failed to load resource: net::ERR_FAILED`
- console: `warning: ⚠️ Backend route API unavailable, falling back to BFS mock: Failed to fetch`
