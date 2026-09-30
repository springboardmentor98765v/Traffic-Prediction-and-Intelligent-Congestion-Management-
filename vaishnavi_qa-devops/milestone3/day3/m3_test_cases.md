# TrafficVision AI — Milestone 3 Test Cases (Day 3)

Owner: Intern 5 (QA) · Date: 2026-09-24 · Source contracts: Alert Service frozen Day 2
(`QA/milestone3/day2/day2_summary.md`). Analytics contract frozen 2026-09-25 by Intern 2
(same file, "Update 2026-09-25"). AI Insights contract not delivered.

Automated suite: `QA/milestone3/tests/` (pytest). Each automated case has a test function whose
name starts with its ID (e.g. `test_tc_al_10_...`).

```
python -m pytest QA/milestone3/tests                 # everything (live tests auto-skip if stack is down)
python -m pytest QA/milestone3/tests -m "not live"   # unit only, no Docker needed
```

Status key: **Auto** = automated and passing · **Auto-xfail** = automated, expected to fail until
the linked defect is fixed (strict: goes red once fixed, so it gets promoted) · **Skeleton** =
test stub waiting on a contract · **Manual** = Postman/manual.

## 1. Alert Service — trigger correctness (unit, no network)

| ID        | Scenario                                                    | Input                                                               | Expected                                                                                                         | Type |
| --------- | ----------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ---- |
| TC-AL-01  | High / Severe congestion triggers an alert                  | watcher reading `congestion_level=High` / `Severe`                  | `alert_triggered=True`, 1 POST sent                                                                              | Auto |
| TC-AL-02  | Low / Medium does not trigger                               | `Low` / `Medium`                                                    | no POST                                                                                                          | Auto |
| TC-AL-03  | Payload matches the frozen contract                         | High on R002                                                        | `{type: congestion, severity: High, road_id: R002, message: "High congestion threshold breached on road R002."}` | Auto |
| TC-AL-04  | Repeated breach deduplicated                                | High then Severe, same road                                         | 2nd: `alert_already_active`, still 1 POST                                                                        | Auto |
| TC-AL-05  | Re-arms after congestion clears                             | High → Low → High                                                   | 2 POSTs                                                                                                          | Auto |
| TC-AL-06  | Failed delivery retried on the next reading                 | 1st send `failed`, 2nd `created`                                    | 2nd reading triggers                                                                                             | Auto |
| TC-AL-07  | Alert URL not configured                                    | empty `ALERT_API_URL`                                               | `status: pending`, no exception                                                                                  | Auto |
| TC-AL-07b | M2 field aliases accepted                                   | `traffic_density` / `timestamp` instead of `density` / `updated_at` | normalised correctly                                                                                             | Auto |
| TC-AL-08a | Baseline-like traffic → normal                              | R001 Tue 08:00, 91 veh, 27 km/h, density 18.3                       | `anomaly_class=normal`                                                                                           | Auto |
| TC-AL-08b | Crash signature → possible_incident (drives accident alert) | 200 veh, 3 km/h, density 60                                         | `possible_incident`                                                                                              | Auto |
| TC-AL-08c | Road with no baseline                                       | R999                                                                | `unknown`, no crash                                                                                              | Auto |

## 2. Alert Service — API functional (live stack)

| ID       | Scenario                                                  | Expected                                                  | Type |
| -------- | --------------------------------------------------------- | --------------------------------------------------------- | ---- |
| TC-AL-10 | POST valid alert                                          | 201, `{alert_id:int, status:"created", road_id, message}` | Auto |
| TC-AL-11 | POST missing each required field                          | 422                                                       | Auto |
| TC-AL-12 | New alert appears in list with all 7 fields, `read=false` | as stated                                                 | Auto |
| TC-AL-13 | List ordering                                             | newest first                                              | Auto |
| TC-AL-14 | PATCH `/{id}/read`                                        | 200 `read:true`, persisted                                | Auto |
| TC-AL-15 | PATCH unknown id                                          | 404                                                       | Auto |

## 3. Alert Service — RBAC-scoped visibility

| ID       | Scenario                                             | Expected                      | Type                    |
| -------- | ---------------------------------------------------- | ----------------------------- | ----------------------- |
| TC-AL-16 | `user` view hides Critical                           | Critical alert not returned   | Auto                    |
| TC-AL-17 | `operator` / `admin` see Critical                    | returned                      | Auto                    |
| TC-AL-18 | `user` still sees Low/Medium/High                    | all three returned            | Auto                    |
| TC-AL-19 | Severity casing (`critical`) still hidden from users | hidden                        | Auto-xfail (DEF-M3-005) |
| TC-AL-20 | List without JWT                                     | 401                           | Auto-xfail (DEF-M3-005) |
| TC-AL-21 | Public user's JWT + `?role=admin`                    | 403, or Critical not returned | Auto-xfail (DEF-M3-005) |
| TC-AL-22 | Create alert without JWT                             | 401/403                       | Auto-xfail (DEF-M3-005) |
| TC-AL-23 | Mark read without JWT                                | 401/403                       | Auto-xfail (DEF-M3-005) |

## 4. Alert Service — delivery timing & reliability

| ID       | Scenario                                                                     | Expected                                         | Type                             |
| -------- | ---------------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------- |
| TC-AL-24 | Created alert visible to user list                                           | within 2 s                                       | Auto                             |
| TC-AL-25 | Latency distribution over 50 alerts (create → visible)                       | p95 < 1 s, 0 lost                                | Manual script (Day 4)            |
| TC-AL-26 | Congestion watcher → live Alert API end-to-end                               | alert stored, dedup holds against real API       | Manual script (Day 4)            |
| TC-AL-27 | Anomaly detector → accident alert end-to-end (`automate_accident_alerts.py`) | `type: accident` stored when `possible_incident` | Manual script (Day 4)            |
| TC-AL-28 | Alerts page (`Front-end/.../Alerts.html`) shows live alerts                  | renders API data                                 | Manual (blocked: page is static) |

## 5. Analytics Service — trend / heatmap accuracy (live, Intern 2's `Data/src/main.py` on :8001)

Contract as delivered by Intern 2 (replaces the Day 3 placeholder cases):
`GET /analytics/trends?road_id=&start_date=&end_date=`,
`GET /analytics/heatmap?start_date=&end_date=&time_bucket=hour|day`,
`GET /analytics/reports?road_id=&start_date=&end_date=&limit=` (CSV). Redis cache, 60 s TTL.
Accuracy oracle: raw rows from `/analytics/reports`, re-aggregated in Python on IST days/hours.

| ID       | Scenario                                               | Expected                                           | Type                    |
| -------- | ------------------------------------------------------ | -------------------------------------------------- | ----------------------- |
| TC-AN-01 | Trend daily series ordered and complete                | 28 unique ascending days, 7×24 weekly pattern      | Auto                    |
| TC-AN-02 | Trend daily values match raw rows (R002)               | readings, avg (±0.01), max equal                   | Auto                    |
| TC-AN-03 | Date filter is inclusive                               | 08-01..08-03 → exactly 3 days                      | Auto                    |
| TC-AN-04 | `road_id` missing                                      | 422                                                | Auto                    |
| TC-AN-05 | Unknown road                                           | 404, not 200 with empty data                       | Auto-xfail (DEF-M3-011) |
| TC-AN-06 | Inverted date range                                    | 400/422                                            | Auto-xfail (DEF-M3-011) |
| TC-AN-07 | Malformed date on trends / heatmap / reports           | 400/422, not 500                                   | Auto-xfail (DEF-M3-009) |
| TC-AN-08 | Heatmap hour grid complete                             | 6 roads × 24 h, no duplicates                      | Auto                    |
| TC-AN-09 | Heatmap hour cells match raw rows                      | readings, avg (±0.01), level counts sum            | Auto                    |
| TC-AN-10 | Heatmap day bucket agrees with trends for the same day | equal                                              | Auto                    |
| TC-AN-11 | Unknown `time_bucket`                                  | 400                                                | Auto                    |
| TC-AN-12 | Report is a CSV download                               | `text/csv`, filename, `X-Report-Row-Count` matches | Auto                    |
| TC-AN-13 | Report `limit` 0 / 50001                               | 400                                                | Auto                    |
| TC-AN-14 | Report for a day covers the same IST day as trends     | only that IST day                                  | Auto-xfail (DEF-M3-010) |
| TC-AN-15 | Response cached with 60 s TTL                          | 1 key, 0 < TTL ≤ 60, identical body                | Auto                    |
| TC-AN-16 | Different params use different cache keys              | 2 keys                                             | Auto                    |
| TC-AN-17 | 4-week queries, cache cold                             | each < 2 s                                         | Auto                    |

## 6. AI Insights — recommendations (waiting on Intern 3)

| ID       | Scenario                                | Expected                      |
| -------- | --------------------------------------- | ----------------------------- |
| TC-AI-01 | Recommendation for High congestion road | non-empty, references road id |
| TC-AI-02 | Required fields present                 | per contract once frozen      |
| TC-AI-03 | Invalid road / payload                  | 4xx, not 500                  |

Anomaly detection (the part of AI Insights that exists today) is covered by TC-AL-08a–c.

## 7. Day 3 checkpoint status

- [x] Test cases written for Alerts (28) and Analytics (8), plus 3 AI Insights placeholders
- [x] Automated testing tool set up: `QA/milestone3/tests/`, pytest, `live` marker auto-skips
      when the stack is down
- [x] Ready to start testing. First run on 2026-09-24: **27 passed, 5 xfailed (DEF-M3-005),
      8 skipped (Analytics)**
- Day 4 update (2026-09-25): Analytics section rewritten against Intern 2's delivered contract
  (17 cases). Full run: **42 passed, 11 xfailed, 0 skipped**.
