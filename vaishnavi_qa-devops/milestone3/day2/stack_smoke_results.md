# Milestone 3 Day 2 — Full Stack Smoke Test Results

Executed 2026-09-24 against the stack started by `docker compose -f docker-compose.dev.yml up -d`.
Command: `python QA/milestone3/day2/stack_smoke_test.py` (run 3 times, identical results).

| Area       | Check                          | Method | Path                                                                           | Expected | Actual | ms   | Result |
| ---------- | ------------------------------ | ------ | ------------------------------------------------------------------------------ | -------- | ------ | ---- | ------ |
| System     | Health                         | GET    | `/health`                                                                      | 200      | 200    | 68   | PASS   |
| M1 Auth    | Register                       | POST   | `/api/v1/auth/register`                                                        | 201      | 201    | 272  | PASS   |
| M1 Auth    | Login                          | POST   | `/api/v1/auth/login`                                                           | 200      | 200    | 466  | PASS   |
| M1 Auth    | Me (with token)                | GET    | `/api/v1/auth/me`                                                              | 200      | 200    | 14   | PASS   |
| M1 Auth    | Me (no token) rejected         | GET    | `/api/v1/auth/me`                                                              | 401      | 401    | 10   | PASS   |
| M1 Auth    | Refresh                        | POST   | `/api/v1/auth/refresh`                                                         | 200      | 200    | 10   | PASS   |
| M1 Auth    | Login wrong password rejected  | POST   | `/api/v1/auth/login`                                                           | 401      | 401    | 313  | PASS   |
| M2 Traffic | Live                           | GET    | `/api/v1/traffic/live`                                                         | 200      | 200    | 11   | PASS   |
| M2 Traffic | Road R001                      | GET    | `/api/v1/traffic/road/R001`                                                    | 200      | 200    | 25   | PASS   |
| M2 Traffic | Density                        | GET    | `/api/v1/traffic/density`                                                      | 200      | 200    | 11   | PASS   |
| M2 Traffic | History                        | GET    | `/api/v1/traffic/history?road_id=R001&limit=5`                                 | 200      | 200    | 11   | PASS   |
| M2 Traffic | Aggregate                      | GET    | `/api/v1/traffic/aggregate?road_id=R001`                                       | 200      | 200    | 12   | PASS   |
| M2 Traffic | Road condition                 | GET    | `/api/v1/traffic/road-condition/R001`                                          | 200      | 200    | 9    | PASS   |
| M2 Traffic | Hourly metrics                 | GET    | `/api/v1/traffic/metrics/hourly?road_id=R001&limit=5`                          | 200      | 200    | 9    | PASS   |
| M2 Traffic | Daily metrics                  | GET    | `/api/v1/traffic/metrics/daily?road_id=R001&limit=5`                           | 200      | 200    | 9    | PASS   |
| M2 Predict | Congestion (GET)               | GET    | `/api/v1/predict/congestion?road_id=R001`                                      | 200      | 200    | 192  | PASS   |
| M2 Predict | Congestion (POST)              | POST   | `/api/v1/predict/congestion`                                                   | 200      | 200    | 186  | PASS   |
| M2 Predict | Peak hours                     | GET    | `/api/v1/predict/peak-hours?road_id=R001`                                      | 200      | 200    | 13   | PASS   |
| M2 Predict | Delay                          | GET    | `/api/v1/predict/delay?road_id=R001`                                           | 200      | 200    | 40   | PASS   |
| M2 Route   | optimize                       | GET    | `/api/v1/route/optimize?origin=11.9416,79.8083&destination=11.9350,79.8100`    | 200      | 200    | 1208 | PASS   |
| M2 Route   | alternate                      | GET    | `/api/v1/route/alternate?origin=11.9416,79.8083&destination=11.9350,79.8100`   | 200      | 500    | 495  | FAIL   |
| M2 Route   | travel-time                    | GET    | `/api/v1/route/travel-time?origin=11.9416,79.8083&destination=11.9350,79.8100` | 200      | 200    | 616  | PASS   |
| M2 Route   | conditions                     | GET    | `/api/v1/route/conditions?origin=11.9416,79.8083&destination=11.9350,79.8100`  | 200      | 200    | 8    | PASS   |
| M2 Route   | No token rejected              | GET    | `/api/v1/route/optimize?origin=11.9416,79.8083&destination=11.9350,79.8100`    | 401      | 401    | 8    | PASS   |
| M2 Route   | Invalid coords rejected        | GET    | `/api/v1/route/optimize?origin=abc&destination=xyz`                            | 400      | 400    | 8    | PASS   |
| M3 Alerts  | Create congestion alert        | POST   | `/api/v1/alerts/`                                                              | 201      | 201    | 15   | PASS   |
| M3 Alerts  | Create critical accident alert | POST   | `/api/v1/alerts/`                                                              | 201      | 201    | 14   | PASS   |
| M3 Alerts  | Missing fields rejected        | POST   | `/api/v1/alerts/`                                                              | 422      | 422    | 10   | PASS   |
| M3 Alerts  | List as user                   | GET    | `/api/v1/alerts/my?role=user`                                                  | 200      | 200    | 14   | PASS   |
| M3 Alerts  | List as admin                  | GET    | `/api/v1/alerts/my?role=admin`                                                 | 200      | 200    | 11   | PASS   |
| M3 Alerts  | Mark read                      | PATCH  | `/api/v1/alerts/7/read`                                                        | 200      | 200    | 26   | PASS   |
| M3 Alerts  | Mark read unknown id -> 404    | PATCH  | `/api/v1/alerts/99999999/read`                                                 | 404      | 404    | 13   | PASS   |
| M3 Alerts  | user view hides Critical       | -      | `(derived)`                                                                    | True     | True   | 0    | PASS   |
| M3 Alerts  | admin view includes Critical   | -      | `(derived)`                                                                    | True     | True   | 0    | PASS   |

33/34 passed
