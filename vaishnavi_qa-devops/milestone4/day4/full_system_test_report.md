# Milestone 4 Day 4 — Full System Test (live environment)

- Run: 2026-10-13 02:50 UTC from HP
- Result: **65/65 passed**, 0 failed, 3 skipped
- Targets: backend `https://trafficvision-ai-i8e2.onrender.com`, analytics `https://trafficvision-ai-i8e2.onrender.com/analytics`, ai `https://trafficvision-ai-i8e2.onrender.com/ai-engine`, web `https://trafficvision-ai-i8e2.onrender.com`

> Cold start / time to first 200: ai 0.6 s, analytics 1.1 s, backend 1.6 s, web 2.2 s

| # | Area | Check | Expected | Actual | ms | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | W1 User journey | Register | 201 | 201 | 2103 | ✅ PASS |
| 2 | W1 User journey | Duplicate register rejected | 409 | 409 | 548 | ✅ PASS |
| 3 | W1 User journey | Login | 200 | 200 | 1988 | ✅ PASS |
| 4 | W1 User journey | Profile (/auth/me) | 200 | 200 | 467 | ✅ PASS |
| 5 | W1 User journey | New account role is PUBLIC | PUBLIC | PUBLIC |  | ✅ PASS |
| 6 | W1 User journey | Refresh token | 200 | 200 | 521 | ✅ PASS |
| 7 | W1 User journey | Dashboard: live traffic | 200 | 200 | 501 | ✅ PASS |
| 8 | W1 User journey | Dashboard: density summary | 200 | 200 | 515 | ✅ PASS |
| 9 | W1 User journey | Road detail R001 | 200 | 200 | 514 | ✅ PASS |
| 10 | W1 User journey | Road condition | 200 | 200 | 609 | ✅ PASS |
| 11 | W1 User journey | History | 200 | 200 | 624 | ✅ PASS |
| 12 | W1 User journey | Aggregate | 200 | 200 | 505 | ✅ PASS |
| 13 | W1 User journey | Hourly metrics | 200 | 200 | 513 | ✅ PASS |
| 14 | W1 User journey | Daily metrics | 200 | 200 | 617 | ✅ PASS |
| 15 | W1 User journey | Predict congestion (GET) | 200 | 200 | 933 | ✅ PASS |
| 16 | W1 User journey | Prediction has a level | non-empty | True |  | ✅ PASS |
| 17 | W1 User journey | Predict congestion (POST) | 200 | 200 | 1117 | ✅ PASS |
| 18 | W1 User journey | Peak hours | 200 | 200 | 614 | ✅ PASS |
| 19 | W1 User journey | Delay estimate | 200 | 200 | 511 | ✅ PASS |
| 20 | W1 User journey | Route optimize | 200 | 200 | 1427 | ✅ PASS |
| 21 | W1 User journey | Route alternate | 200 | 200 | 1538 | ✅ PASS |
| 22 | W1 User journey | Route travel-time | 200 | 200 | 1032 | ✅ PASS |
| 23 | W1 User journey | Route conditions | 200 | 200 | 581 | ✅ PASS |
| 24 | W1 User journey | My alerts | 200 | 200 | 539 | ✅ PASS |
| 25 | W2 Operator | Operator account | operator | no DATABASE_URL to promote |  | ⏭ SKIP |
| 26 | W2 Operator | Analytics trends | 200 | 200 | 888 | ✅ PASS |
| 27 | W2 Operator | Trends has daily data | non-empty | 28 |  | ✅ PASS |
| 28 | W2 Operator | Heatmap (hourly) | 200 | 200 | 666 | ✅ PASS |
| 29 | W2 Operator | Heatmap (daily) | 200 | 200 | 582 | ✅ PASS |
| 30 | W2 Operator | Report export (CSV) | 200 text/csv | 200 text/csv; charset=utf-8 | 724 | ✅ PASS |
| 31 | W2 Operator | Analytics traffic/live | 200 | 200 | 8807 | ✅ PASS |
| 32 | W2 Operator | Analytics traffic/road/R001 | 200 | 200 | 620 | ✅ PASS |
| 33 | W2 Operator | Analytics traffic/density | 200 | 200 | 507 | ✅ PASS |
| 34 | W2 Operator | Analytics traffic/history | 200 | 200 | 613 | ✅ PASS |
| 35 | W4 Alert pipeline | Producer posts alerts | 201 | ALERT_SERVICE_KEY not set |  | ⏭ SKIP |
| 36 | W4 Alert pipeline | Post without key/token rejected | 403 | 403 | 1581 | ✅ PASS |
| 37 | W4 Alert pipeline | User reads alerts | 200 | 200 | 1188 | ✅ PASS |
| 38 | W4 Alert pipeline | User view hides Critical/accident | 0 | 0 |  | ✅ PASS |
| 39 | W3 Admin | Admin account | admin | no DATABASE_URL to promote |  | ⏭ SKIP |
| 40 | W5 AI insights | AI root | 200 | 200 | 409 | ✅ PASS |
| 41 | W5 AI insights | Anomalies (all roads) | 200 | 200 | 28726 | ✅ PASS |
| 42 | W5 AI insights | Anomalies returned data | non-empty | list |  | ✅ PASS |
| 43 | W5 AI insights | Anomalies R001 | 200 | 200 | 5931 | ✅ PASS |
| 44 | W5 AI insights | Recommendations R001 | 200 | 200 | 1022 | ✅ PASS |
| 45 | W5 AI insights | Manual prediction | 200 | 200 | 612 | ✅ PASS |
| 46 | W5 AI insights | Live prediction (AI -> backend) | 200 | 200 | 515 | ✅ PASS |
| 47 | W5 AI insights | Congestion by road (AI -> backend) | 200 | 200 | 524 | ✅ PASS |
| 48 | W6 Consistency | Backend and analytics see same roads | ['R001', 'R002', 'R003', 'R004', 'R005', 'R006'] | ['R001', 'R002', 'R003', 'R004', 'R005', 'R006'] |  | ✅ PASS |
| 49 | W7 Negative | Wrong password -> 401 | 401 | 401 | 1950 | ✅ PASS |
| 50 | W7 Negative | Unknown user -> 401 | 401 | 401 | 507 | ✅ PASS |
| 51 | W7 Negative | Disallowed email domain -> 422 | 422 | 422 | 487 | ✅ PASS |
| 52 | W7 Negative | /auth/me without token -> 401 | 401 | 401 | 537 | ✅ PASS |
| 53 | W7 Negative | /auth/me bad token -> 401 | 401 | 401 | 409 | ✅ PASS |
| 54 | W7 Negative | Route without token -> 401 | 401 | 401 | 410 | ✅ PASS |
| 55 | W7 Negative | Route bad coords -> 400 | 400 | 400 | 410 | ✅ PASS |
| 56 | W7 Negative | Alerts without token -> 401 | 401 | 401 | 511 | ✅ PASS |
| 57 | W7 Negative | Trends unknown road -> 404 | 404 | 404 | 514 | ✅ PASS |
| 58 | W7 Negative | Trends malformed date -> 422 | 422 | 422 | 522 | ✅ PASS |
| 59 | W7 Negative | Trends inverted range -> 400 | 400 | 400 | 423 | ✅ PASS |
| 60 | W7 Negative | AI recommendations unknown road -> 404 | 404 | 404 | 486 | ✅ PASS |
| 61 | W8 Frontend | Login.html | 200 | 200 | 522 | ✅ PASS |
| 62 | W8 Frontend | public dashboard.html | 200 | 200 | 475 | ✅ PASS |
| 63 | W8 Frontend | operator dashboard.html | 200 | 200 | 459 | ✅ PASS |
| 64 | W8 Frontend | admin dashboard.html | 200 | 200 | 599 | ✅ PASS |
| 65 | W8 Frontend | live maps.html | 200 | 200 | 523 | ✅ PASS |
| 66 | W8 Frontend | route-analysis.html | 200 | 200 | 615 | ✅ PASS |
| 67 | W8 Frontend | Alerts.html | 200 | 200 | 507 | ✅ PASS |
| 68 | W8 Frontend | analytics.html | 200 | 200 | 934 | ✅ PASS |
