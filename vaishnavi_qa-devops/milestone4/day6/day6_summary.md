# Milestone 4 Day 6 — Final regression + stability sign-off

`final_regression.py` re-runs smoke, full-system, Selenium UI (when Selenium is installed)
and performance; compares with the Day 4/5 JSON baselines (PASS → FAIL, or p95 more than
50 % and 200 ms slower); then probes every service's health path for a stability window.

**Sign-off rule:** 0 functional FAIL, 0 regressions, 0 API/availability errors, at least
99 % of health probes OK.

Rehearsal: the script ran end to end locally and correctly flagged a latency regression
(AI recommendations p95 293 → 1077 ms) and the local-only page failures, so it blocks
sign-off when it should.

## Pending (live)

- [ ] After the Day 5/6 fixes are deployed:
      `python QA/milestone4/day6/final_regression.py --stability-minutes 10 --report QA/milestone4/day6/final_regression_report.md`
- [ ] Sign-off line in the report reads ✅ STABLE
