# Milestone 4 Day 5 — Performance checks + defect list

`performance_check.py` measures cold start, warm latency (p50/p95/max on 16 endpoints),
concurrency (10 users × 5 requests on the 3 busiest reads) and page delivery, then ends the
report with a prioritised defect list (PERF-xx).

Thresholds (free tier): API p95 ≤ 1000 ms, heavy AI/ML ≤ 2500 ms, under load ≤ 3000 ms,
pages ≤ 2000 ms, 0 errors.

## Rehearsal findings (local, 2026-10-07)

| Finding                                              | Defect     |
| ---------------------------------------------------- | ---------- |
| Route optimize p95 4.3 s (external OSRM call)        | DEF-M4-012 |
| AI recommendations p95 3.7 s with 5 concurrent users | DEF-M4-013 |

Everything else was well inside the limits (most endpoints under 100 ms locally). Expect
higher numbers on Render's shared CPU — the live run is the one that counts.

## Pending (live)

- [ ] Run after at least 15 minutes idle to capture real cold starts
- [ ] Save `performance_report.md` + `performance_results.json` here; copy PERF rows into the tracker
