# Milestone 4 Day 6 — Final Regression Report & Stability Sign-off

- Run: 2026-10-13 12:12 UTC, from GitHub Actions ([Live QA run 38394129591](https://github.com/deekshuu09-sudo/TrafficVision-AI/actions/runs/38394129591), commit `86c2748`)
- Targets: backend `https://trafficvision-ai-i8e2.onrender.com`, analytics `https://trafficvision-ai-i8e2.onrender.com/analytics`, ai `https://trafficvision-ai-i8e2.onrender.com/ai-engine`, web `https://trafficvision-ai-i8e2.onrender.com`
- Baselines: Day 4 found, Day 5 found

## Sign-off: ✅ STABLE — approved for final demo

| Criterion | Result |
| --- | --- |
| Functional suites: 0 FAIL | 0 FAIL |
| No regressions vs Day 4 / Day 5 | 0 found |
| No API/availability errors under load | 0 found |
| Health probes >= 99 % over 10 min | 100.0 % (84/84) |

## 1. Functional regression

| Suite | PASS | FAIL | SKIP |
| --- | --- | --- | --- |
| Smoke (Day 3 suite) | 32 | 0 | 0 |
| Full system (Day 4 suite) | 65 | 0 | 3 |
| Selenium UI (Chrome) | 67 | 0 | 2 |

The 3 full-system skips are operator/admin checks that need database access to promote QA accounts.

## 2. Regressions

None.

## 3. Performance (re-run)

| Service | Endpoint | p95 now (ms) | Limit |
| --- | --- | --- | --- |
| backend | Health | 77 | 1000 |
| backend | Live traffic | 162 | 1000 |
| backend | Road detail | 101 | 1000 |
| backend | Density | 79 | 1000 |
| backend | Hourly metrics | 77 | 1000 |
| backend | Auth /me | 82 | 1000 |
| backend | My alerts | 88 | 1000 |
| backend | Predict congestion | 403 | 2500 |
| backend | Route optimize | 907 | 2500 |
| analytics | Analytics live | 209 | 1000 |
| analytics | Trends | 198 | 1000 |
| analytics | Heatmap | 87 | 1000 |
| analytics | Report CSV | 335 | 1000 |
| ai | AI health | 91 | 1000 |
| ai | Anomalies | 92 | 2500 |
| ai | Recommendations | 82 | 2500 |

Open performance findings: 0.

## 4. Stability window

| Service | Probes OK | Worst response (ms) |
| --- | --- | --- |
| backend | 21/21 | 109 |
| analytics | 21/21 | 109 |
| ai | 21/21 | 115 |
| web | 21/21 | 138 |

## Notes

- Runs from the QA laptop on 2026-10-13 were not usable for sign-off: the home connection was unstable
  (google.com 2.5–6.5 s, one outage at ~13:25 IST), so the suite now runs from GitHub's network via
  the Live QA workflow in the deploy repo.
- The last fix before sign-off: `analytics.html` overflowed 149 px at exactly 768 px on Linux Chrome
  (AI recommendations header could not wrap) — fixed in `86c2748`.
