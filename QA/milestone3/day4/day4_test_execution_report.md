# Milestone 3 — Day 4 Test Execution Report (Intern 5)

Dates: 2026-09-24 (Alert Service), 2026-09-25 (Analytics Service + full re-run)
Environment: `docker-compose.dev.yml` stack. 4 containers healthy: `backend` (gateway + Alert
Service, :8000), `analytics` (Intern 2's `Data/src/main.py`, :8001), TimescaleDB, Redis. Image
`trafficvision-backend:dev`. Analytics data loaded with `QA/milestone3/day6/analytics_setup.sh`:
`traffic_history` 4,032 rows (6 roads × 28 days × 24 h), `hourly_traffic_metrics` 4,032,
`daily_traffic_metrics` 174.

## Checkpoints

- [x] **Alert & Analytics features tested.** Alerts: 32 automated tests plus 3 end-to-end script checks.
      Analytics: 17 cases (21 test runs incl. parametrised), all executed. Nothing skipped.
- [x] **Alert delivery timing checked.** 50/50 delivered, 0 lost, p95 96 ms (target < 1 s).
- [x] **Bugs logged with priority.** Alerts: DEF-M3-005 (High), DEF-M3-007 (Medium), DEF-M3-008
      (Low). Analytics: DEF-M3-009 (Medium/High), DEF-M3-010 (Medium), DEF-M3-011 (Low). All in
      `../day1/defect_tracker.md`.

## 1. Automated suite: `python -m pytest QA/milestone3/tests`

2026-09-25, full stack up:

```
42 passed, 11 xfailed in 26.52s        (0 skipped; re-run twice, identical)
```

(Day 4 first run on 2026-09-24, before Analytics was deployed: 27 passed, 5 xfailed, 8 skipped.)

| Group                                                  | Tests  | Pass   | Xfail (known defect)             |
| ------------------------------------------------------ | ------ | ------ | -------------------------------- |
| Trigger correctness: congestion watcher (TC-AL-01…07b) | 10     | 10     | –                                |
| Trigger correctness: anomaly detector (TC-AL-08a–c)    | 3      | 3      | –                                |
| Alert API functional (TC-AL-10…15)                     | 9      | 9      | –                                |
| Role-scoped visibility as implemented (TC-AL-16…18)    | 4      | 4      | –                                |
| RBAC per SRS, JWT-based (TC-AL-19…23)                  | 5      | –      | 5 (DEF-M3-005)                   |
| Delivery timing (TC-AL-24)                             | 1      | 1      | –                                |
| Analytics trends (TC-AN-01…07)                         | 9      | 4      | 5 (DEF-M3-009 ×3, DEF-M3-011 ×2) |
| Analytics heatmap (TC-AN-08…11)                        | 4      | 4      | –                                |
| Analytics reports (TC-AN-12…14)                        | 4      | 3      | 1 (DEF-M3-010)                   |
| Analytics caching + performance (TC-AN-15…17)          | 4      | 4      | –                                |
| **Total**                                              | **53** | **42** | **11**                           |

Xfails are strict, so each one goes red as soon as its defect is fixed and then gets promoted to
a normal test.

## 2. Alert delivery timing & end-to-end producers: `python QA/milestone3/day4/alert_delivery_check.py`

Re-run 2026-09-25:

| ID       | Check                                                                 | Result                                                                                           | Verdict                 |
| -------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------- |
| TC-AL-25 | 50 alerts, create → visible in `role=user` list                       | delivered 50/50, lost 0, **p50 58 ms, p95 96 ms, max 2,324 ms**                                  | PASS (target p95 < 1 s) |
| TC-AL-26 | Congestion watcher → live Alert API                                   | first High triggers; follow-up → `alert_already_active`; exactly 1 row stored                    | PASS                    |
| TC-AL-27 | Anomaly detector → accident alert                                     | 200 veh / 3 km/h / density 60 on R001 → `possible_incident` (score 1.43) → 201, 1 `accident` row | PASS                    |
| —        | Intern 3's `automate_accident_alerts.py`, run as shipped (2026-09-24) | `possible_incident` → alert created                                                              | PASS                    |

The single 2.3 s outlier (Day 1 run max was 251 ms) came right after a cold stack start. p95 is
unaffected. It's worth watching in the Day 5 integration run but isn't logged as a defect.

## 3. Analytics results in detail

| Area                                  | What was verified                                                                                                                                      | Result                                                |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| **Trend accuracy**                    | R002 daily trends re-computed from the raw report rows on IST days: reading counts, average (±0.01, half-up rounding like Postgres), max vehicle count | Exact match for all 28 days                           |
| **Heatmap accuracy**                  | All 144 hour cells (6 roads × 24 h) re-computed from raw rows; Low+Medium+High+Severe counts sum to total readings                                     | Exact match                                           |
| **Cross-endpoint consistency**        | Heatmap `day` bucket vs trends for R001 on 2026-08-01                                                                                                  | Equal                                                 |
| **Report export**                     | `text/csv`, `Content-Disposition` filename, `X-Report-Row-Count` equals rows returned, road filter honoured, `limit` 0/50001 → 400                     | PASS                                                  |
| **Caching**                           | One Redis key per request, `0 < TTL ≤ 60`, cached body identical to the live one, different params → different keys                                    | PASS                                                  |
| **Performance (4 weeks, cache cold)** | heatmap hour, heatmap day, trends R004, full report (4,032 rows)                                                                                       | Each < 2 s; slowest test 0.86 s for all four together |
| **Input validation**                  | Malformed dates, unknown road, inverted range                                                                                                          | **FAIL** → DEF-M3-009, DEF-M3-011                     |
| **Timezone consistency**              | Report for a day vs trends for the same day                                                                                                            | **FAIL** → DEF-M3-010                                 |

## 4. Findings

### Alert Service (2026-09-24, re-confirmed 2026-09-25)

1. **RBAC is not enforced by the server (DEF-M3-005, High).** Alert visibility depends on a
   `?role=` value the client sends, and no alert endpoint requires a JWT.
2. **Accident alerts are visible to public users (DEF-M3-007, Medium).** Re-confirmed today:
   TC-AL-27 shows `visible_to_user: true`. Needs a product decision: filter on
   `type == "accident"`, or have producers send `Critical`.
3. **Severity vocabulary mismatch (DEF-M3-008, Low).** The watcher sends `"Severe"`, which is
   outside Low/Medium/High/Critical and isn't validated.
4. The watcher's dedup set lives in memory, so a restart re-sends alerts for roads that are
   still congested. Noted for Day 5.

### Analytics Service (2026-09-25)

5. **Malformed dates crash the service (DEF-M3-009, Medium / High priority).** `start_date=abc`
   on trends, `2026-13-45` on heatmap and `notadate` on reports all return **500**. Date params
   are untyped strings passed straight into `::date` casts, and only `ValueError` is handled.
   Fix: declare them as `datetime.date | None`.
6. **Reports use UTC days, the dashboard uses IST days (DEF-M3-010, Medium).**
   `report_service.py` filters on raw `reading_timestamp`, but trends and heatmap bucket
   `AT TIME ZONE 'Asia/Kolkata'`. A "2026-08-01" report runs from 05:30 IST Aug 1 to 05:29 IST
   Aug 2, so a CSV export won't reconcile with the chart the user just saw.
7. **No 404/400 for unknown road or inverted range (DEF-M3-011, Low).** Both return 200 with
   empty arrays.
8. Positive: trend and heatmap numbers match the source data exactly, caching behaves as
   specified, and 4-week queries run well inside the < 2 s target even with a cold cache.

## 5. Not executed (blocked on other interns)

| Case                                                                                      | Blocker                                                                                                     | Owner               |
| ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------- |
| TC-AL-28: Alerts page shows live alerts                                                   | `Frontend/Front-end/Alerts.html` still has no `fetch` calls (`alertsAPI` exists in `api.js` but isn't used) | Intern 4 (Frontend) |
| TC-AI-01…03: recommendations                                                              | No AI Insights HTTP endpoint or contract. `anomaly_detector.py` is library-only (covered by TC-AL-08a–c)    | Intern 3 (AI)       |
| SRS "First Vertical Slice" checkpoint (alerts reachable end-to-end **from the frontend**) | Same as TC-AL-28                                                                                            | Intern 4 + Intern 1 |

## 6. Defect summary for Interns 1 & 2 (fix list)

| Defect     | Severity | Priority | Owner          | One-line fix                                                                          |
| ---------- | -------- | -------- | -------------- | ------------------------------------------------------------------------------------- |
| DEF-M3-005 | High     | High     | Intern 1       | Add `get_current_user` to all alert routes; take role from the JWT, not `?role=`      |
| DEF-M3-009 | Medium   | High     | Intern 2       | Type `start_date`/`end_date` as `date` in all 3 analytics routes                      |
| DEF-M3-007 | Medium   | Medium   | Intern 1 + 3   | Decide whether accidents are operator/admin only; filter on `type` or send `Critical` |
| DEF-M3-010 | Medium   | Medium   | Intern 2       | Filter reports on `(reading_timestamp AT TIME ZONE 'Asia/Kolkata')::date`             |
| DEF-M3-008 | Low      | Medium   | Intern 1 + 2/3 | Enum-validate `severity`/`type`; map Severe → Critical in the watcher                 |
| DEF-M3-011 | Low      | Medium   | Intern 2       | 404 for unknown road, 400 when `start_date > end_date`                                |

## Reproduce

```
docker compose -f docker-compose.dev.yml up -d
bash QA/milestone3/day6/analytics_setup.sh          # one-time analytics data load
python -m pytest QA/milestone3/tests -rxX
python QA/milestone3/day4/alert_delivery_check.py
```

Test data note: tests write alerts to the dev DB under unique road ids (`QA-…`, `QA-LAT-…`,
`QA-W-…`) plus a few on R001–R003. To reset:
`docker exec trafficvision-postgres-dev psql -U traffic -d trafficvision -c "DELETE FROM alerts WHERE road_id LIKE 'QA-%';"`
Analytics tests are read-only apart from flushing `traffic:analytics:*` keys in Redis.
