# Milestone 4 Day 6 — Final Regression Report & Stability Sign-off

- Run: 2026-10-13 06:40 UTC
- Targets: backend `https://trafficvision-ai-i8e2.onrender.com`, analytics `https://trafficvision-ai-i8e2.onrender.com/analytics`, ai `https://trafficvision-ai-i8e2.onrender.com/ai-engine`, web `https://trafficvision-ai-i8e2.onrender.com`
- Baselines: Day 4 found, Day 5 found

## Sign-off: ❌ NOT signed off

| Criterion | Result |
| --- | --- |
| Functional suites: 0 FAIL | 0 FAIL |
| No regressions vs Day 4 / Day 5 | 10 found |
| No API/availability errors under load | 0 found |
| Health probes >= 99 % over 10 min | 100.0 % (68/68) |

## 1. Functional regression

| Suite | PASS | FAIL | SKIP |
| --- | --- | --- | --- |
| Smoke (Day 3 suite) | 32 | 0 | 0 |
| Full system (Day 4 suite) | 65 | 0 | 3 |
| Selenium UI (Chrome) | 67 | 0 | 2 |

Full tables: `smoke_results.json`, `full_system_results.json` in this folder.

## 2. Regressions

| Type | Item | Before | Now |
| --- | --- | --- | --- |
| Performance | backend Health | p95 803 ms | p95 5212 ms |
| Performance | backend Live traffic | p95 570 ms | p95 3790 ms |
| Performance | backend Road detail | p95 675 ms | p95 3592 ms |
| Performance | backend Density | p95 518 ms | p95 3035 ms |
| Performance | backend Route optimize | p95 1586 ms | p95 2445 ms |
| Performance | analytics Analytics live | p95 629 ms | p95 2663 ms |
| Performance | analytics Heatmap | p95 597 ms | p95 2090 ms |
| Performance | analytics Report CSV | p95 1101 ms | p95 2670 ms |
| Performance | ai AI health | p95 592 ms | p95 1955 ms |
| Performance | ai Recommendations | p95 529 ms | p95 827 ms |

## 3. Performance (re-run)

| Service | Endpoint | p95 now (ms) | Limit |
| --- | --- | --- | --- |
| backend | Health | 5212 | 1000 |
| backend | Live traffic | 3790 | 1000 |
| backend | Road detail | 3592 | 1000 |
| backend | Density | 3035 | 1000 |
| backend | Hourly metrics | 820 | 1000 |
| backend | Auth /me | 814 | 1000 |
| backend | My alerts | 1011 | 1000 |
| backend | Predict congestion | 1232 | 2500 |
| backend | Route optimize | 2445 | 2500 |
| analytics | Analytics live | 2663 | 1000 |
| analytics | Trends | 1332 | 1000 |
| analytics | Heatmap | 2090 | 1000 |
| analytics | Report CSV | 2670 | 1000 |
| ai | AI health | 1955 | 1000 |
| ai | Anomalies | 4555 | 2500 |
| ai | Recommendations | 827 | 2500 |

Open performance findings: 19 (see `performance_results.json`).

## 4. Stability window

| Service | Probes OK | Worst response (ms) |
| --- | --- | --- |
| backend | 17/17 | 4247 |
| analytics | 17/17 | 3801 |
| ai | 17/17 | 3689 |
| web | 17/17 | 3600 |
