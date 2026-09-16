# Day 4 — Functional Test Execution (Milestone 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Per SRS Section 10.5 Day 4: "Execute functional tests against Route Analysis and Prediction Service as they land; sanity-check prediction response times (~1–2s target); log defects."

**Note on organization:** this work was actually done across two sessions (initial pass before the backend was runnable, then a full live re-pass after DEF-M2-002/003/004 were fixed) and got recorded in the Day 2 and Day 6 docs at the time. This file consolidates it into its own Day 4 record, as it should have been from the start.

## Pass 1 — before the backend could run (see `QA/milestone2/day2/milestone2_day2_test_execution_report.md`)
- pytest run against the backend: blocked, then failing, as DEF-M2-001 through 004 were found.
- Full 16-step browser automation against the frontend, using mock fallback data (backend unreachable at the time).
- Result: 16/18 UI cases passed on mock data; DEF-M2-007 found (stale route data — later re-tested, see below).

## Pass 2 — live, once the backend actually started (see `QA/milestone2/day6/milestone2_day6_regression_report.md`)
Every contract endpoint hit directly against the running backend:

| Endpoint | Result |
|---|---|
| Auth (register/login/me) | Fail against contract path at the time (DEF-M2-002, since fixed) |
| Traffic (live/road/density) | Fail against contract path at the time (DEF-M2-003, since fixed) |
| Route optimize/alternate | Fail against contract path at the time (DEF-M2-004, since fixed); **logic itself worked** once routed around the bug and authenticated — 200 OK, real OSM data |
| Predict congestion | 405 against contract (GET expected, POST actual) — DEF-M2-005, still open |
| Predict peak-hours/delay | 404 — not implemented, still open |
| Historical data (history/aggregate/road-condition) | 404 — not merged from Intern 2's service, still open |

**Latency sanity-check (the ~1–2s target):** `route/optimize` first authenticated call took 5+ seconds (cold start, likely first external OSM lookup); immediate retry succeeded in 0.93s, within target. Flagged to Intern 1 as a cold-start concern worth a warm-up call, not a hard defect.

## Pass 3 — after the 2026-09-13 redelivery (see `QA/milestone2/day7/milestone2_day4_5_7_reverification.md`)
Re-ran every endpoint live again: DEF-M2-002/003/004 confirmed fixed. Attempting the full real login → app flow (not just curl) surfaced three new defects — DEF-M2-016, 017, 018 — that block Day 5, detailed in the Day 7 doc.

## Overall Status
Day 4 is materially complete for everything that currently exists in the backend. What's tested, has a clear pass/fail verdict backed by live evidence across 3 separate passes as the code changed. What's still blocked (historical data, peak-hours, delay, and now the frontend integration bugs) is blocked on specific, named owners — not on QA. See `QA/milestone2/day1/defect_tracker.md` for the full list (DEF-M2-001 through 018).
