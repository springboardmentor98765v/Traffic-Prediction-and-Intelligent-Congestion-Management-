# Milestone 4 Day 5 — Performance Report (live environment)

- Run: 2026-10-13 03:25 UTC
- Targets: backend `https://trafficvision-ai-i8e2.onrender.com`, analytics `https://trafficvision-ai-i8e2.onrender.com/analytics`, ai `https://trafficvision-ai-i8e2.onrender.com/ai-engine`, web `https://trafficvision-ai-i8e2.onrender.com`
- Thresholds: API p95 <= 1000 ms (heavy AI/ML <= 2500 ms), p95 under 10 users <= 3000 ms, page <= 2000 ms, 0 errors
- Verdict: **5 finding(s)**

## 1. Cold start (free tier sleeps after 15 min idle)

| Service | Time to first 200 (s) |
| --- | --- |
| ai | 0.4 |
| analytics | 1.3 |
| backend | 1.6 |
| web | 2.0 |

Only a real cold start if the run began after at least 15 minutes of no traffic.

## 2. Warm API latency (20 sequential requests, ms)

| Service | Endpoint | p50 | p95 | max | Errors | Limit | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| backend | Health | 386 | 803 | 803 | 0 | 1000 | ✅ |
| backend | Live traffic | 392 | 570 | 570 | 0 | 1000 | ✅ |
| backend | Road detail | 457 | 675 | 675 | 0 | 1000 | ✅ |
| backend | Density | 410 | 518 | 518 | 0 | 1000 | ✅ |
| backend | Hourly metrics | 386 | 853 | 853 | 0 | 1000 | ✅ |
| backend | Auth /me | 416 | 695 | 695 | 0 | 1000 | ✅ |
| backend | My alerts | 568 | 710 | 710 | 0 | 1000 | ✅ |
| backend | Predict congestion | 789 | 865 | 865 | 0 | 2500 | ✅ |
| backend | Route optimize | 1308 | 1586 | 1586 | 0 | 2500 | ✅ |
| analytics | Analytics live | 398 | 629 | 629 | 0 | 1000 | ✅ |
| analytics | Trends | 603 | 1198 | 1198 | 0 | 1000 | ❌ |
| analytics | Heatmap | 489 | 597 | 597 | 0 | 1000 | ✅ |
| analytics | Report CSV | 597 | 1101 | 1101 | 0 | 1000 | ❌ |
| ai | AI health | 374 | 592 | 592 | 0 | 1000 | ✅ |
| ai | Anomalies | 377 | 3395 | 3395 | 0 | 2500 | ❌ |
| ai | Recommendations | 411 | 529 | 529 | 0 | 2500 | ✅ |

## 3. Concurrency (10 users x 5 requests)

| Service | Endpoint | p50 | p95 | req/s | Errors | Result |
| --- | --- | --- | --- | --- | --- | --- |
| backend | Live traffic | 433 | 882 | 16.9 | 0 | ✅ |
| analytics | Trends | 3214 | 4893 | 2.9 | 0 | ❌ |
| ai | Recommendations | 448 | 768 | 16.7 | 0 | ✅ |

## 4. Page delivery (HTML/JS download from the static host)

| Page | Status | ms | Size (KB) | Result |
| --- | --- | --- | --- | --- |
| Login.html | 200 | 735 | 52.3 | ✅ |
| public dashboard.html | 200 | 496 | 28.7 | ✅ |
| operator dashboard.html | 200 | 424 | 56.1 | ✅ |
| admin dashboard.html | 200 | 3467 | 63.4 | ❌ |
| live maps.html | 200 | 672 | 49.7 | ✅ |
| route-analysis.html | 200 | 669 | 73.9 | ✅ |
| Alerts.html | 200 | 374 | 50.9 | ✅ |
| analytics.html | 200 | 476 | 124.2 | ✅ |
| api.js | 200 | 464 | 142.3 | ✅ |

Browser rendering (Tailwind CDN, Chart.js, Leaflet) is not included; measure it with
Chrome DevTools -> Lighthouse on each page (Intern 4's cross-browser pass).

## 5. Defect list (prioritised)

| # | Priority | Area | Item | Measured | Expected |
| --- | --- | --- | --- | --- | --- |
| PERF-01 | Medium | API latency | analytics Trends | p95 1198 ms | <= 1000 ms |
| PERF-02 | Medium | API latency | analytics Report CSV | p95 1101 ms | <= 1000 ms |
| PERF-03 | Medium | API latency | ai Anomalies | p95 3395 ms | <= 2500 ms |
| PERF-04 | Medium | Load latency | analytics Trends | p95 4893 ms | <= 3000 ms |
| PERF-05 | Medium | Page load | admin dashboard.html | 200, 3467 ms | 200, <= 2000 ms |

Copy these into QA/milestone4/day1/defect_tracker.md as DEF-M4-0xx with an owner.
