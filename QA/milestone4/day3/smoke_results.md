# Milestone 4 Day 3 — Live Smoke Test

- Run: 2026-10-13 02:51 UTC from HP
- Result: **31/32 passed**, 1 failed, 0 skipped
- Targets: backend `https://trafficvision-ai-i8e2.onrender.com`, analytics `https://trafficvision-ai-i8e2.onrender.com/analytics`, ai `https://trafficvision-ai-i8e2.onrender.com/ai-engine`, web `https://trafficvision-ai-i8e2.onrender.com`

> Time to first 200 (includes free-tier cold start when asleep): ai 0.7 s, analytics 1.2 s, backend 1.7 s, web 2.4 s

| # | Area | Check | Expected | Actual | ms | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Availability | ai reachable | 200 | 0.7 s |  | ✅ PASS |
| 2 | Availability | analytics reachable | 200 | 1.2 s |  | ✅ PASS |
| 3 | Availability | backend reachable | 200 | 1.7 s |  | ✅ PASS |
| 4 | Availability | web reachable | 200 | 2.4 s |  | ✅ PASS |
| 5 | Backend | GET /health | 200 | 200 | 898 | ✅ PASS |
| 6 | Backend | OpenAPI docs | 200 | 200 | 443 | ✅ PASS |
| 7 | Backend | Live traffic (DB read) | 200 | 200 | 478 | ✅ PASS |
| 8 | Backend | Live traffic has rows | > 0 rows | 6 |  | ✅ PASS |
| 9 | Backend | Register + login (DB write, JWT) | token | True |  | ✅ PASS |
| 10 | Backend | GET /auth/me with token | 200 | 200 | 519 | ✅ PASS |
| 11 | Backend | Prediction (model loaded) | 200 | 200 | 906 | ✅ PASS |
| 12 | Analytics | GET / | 200 | 200 | 453 | ✅ PASS |
| 13 | Analytics | Trends R001 (DB) | 200 | 200 | 848 | ✅ PASS |
| 14 | Analytics | Live traffic (Redis/DB) | 200 | 200 | 8254 | ✅ PASS |
| 15 | AI Engine | GET /health | 200 | 200 | 1604 | ✅ PASS |
| 16 | AI Engine | Recommendations R001 | 200 | 200 | 1233 | ✅ PASS |
| 17 | AI Engine | Congestion via backend | 200 | 200 | 819 | ✅ PASS |
| 18 | Frontend | Login.html | 200 | 200 | 632 | ✅ PASS |
| 19 | Frontend | public dashboard.html | 200 | 200 | 1430 | ✅ PASS |
| 20 | Frontend | operator dashboard.html | 200 | 200 | 1340 | ✅ PASS |
| 21 | Frontend | admin dashboard.html | 200 | 200 | 527 | ✅ PASS |
| 22 | Frontend | live maps.html | 200 | 200 | 527 | ✅ PASS |
| 23 | Frontend | route-analysis.html | 200 | 200 | 1133 | ✅ PASS |
| 24 | Frontend | Alerts.html | 200 | 200 | 862 | ✅ PASS |
| 25 | Frontend | analytics.html | 200 | 200 | 708 | ✅ PASS |
| 26 | Frontend | api.js | 200 | 200 | 865 | ✅ PASS |
| 27 | Frontend | / rewrites to Login | 200 | 200 | 812 | ✅ PASS |
| 28 | Frontend | api.js points at production backend | https://trafficvision-ai-i8e2.onrender.com | same origin |  | ✅ PASS |
| 29 | CORS | Frontend origin allowed | https://trafficvision-ai-i8e2.onrender.com | https://trafficvision-ai-i8e2.onrender.com |  | ✅ PASS |
| 30 | CORS | Foreign origin blocked | no ACAO header | https://evil.example |  | ❌ FAIL |
| 31 | Security | Protected route needs token | 401 | 401 | 441 | ✅ PASS |
| 32 | Security | Served over HTTPS | https |  |  | ✅ PASS |
