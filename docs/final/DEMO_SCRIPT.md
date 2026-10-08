# TrafficVision AI — Final Live Demo Script (≈12 minutes)

## T-10 minutes: warm-up (free tier sleeps after 15 min idle)

1. Open in tabs: the frontend, `…backend…/health`, `…analytics…/`, `…ai…/health`. Wait for
   all four to answer (first one can take ~60 s).
2. GitHub → Actions → **Live QA** → `smoke` → Run. Keep the green run open as evidence.
3. Have three accounts ready: a public user, an operator and an admin
   (register in the UI; promote with `UPDATE users SET role='operator' WHERE email='…'`).

## Flow

| #   | Time  | Who speaks | Show                                                                                                                              | Say                                                         |
| --- | ----- | ---------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 1   | 0:00  | Team lead  | Architecture diagram (`docs/final/ARCHITECTURE.md`)                                                                               | 4 services on Render free tier, Postgres, Redis, CI/CD      |
| 2   | 1:00  | Intern 4   | Login page on desktop, then phone width (DevTools)                                                                                | Responsive, CAPTCHA, role tabs                              |
| 3   | 2:00  | Intern 1   | Sign in as **public** → public dashboard with live roads                                                                          | JWT auth, role-based landing page                           |
| 4   | 3:00  | Intern 2   | Live maps → congestion colours; Analytics page → trends, heatmap, **download CSV report**                                         | Live data from Postgres, Redis cache, 4 weeks of history    |
| 5   | 5:00  | Intern 3   | Route analysis: origin `11.9416,79.8083` → destination `11.9350,79.8100`; AI recommendations                                      | Congestion-aware routing with model-v1; anomaly detection   |
| 6   | 7:00  | Intern 1   | Sign in as **operator** → operator dashboard → Alerts                                                                             | Operators see High/Critical alerts; public users don't      |
| 7   | 8:00  | Intern 5   | Swagger `/docs` → `POST /api/v1/alerts/` with the service key → alert appears for operator/admin                                  | Automated alert pipeline                                    |
| 8   | 9:00  | Intern 5   | GitHub Actions: CI/CD run (lint → build → test → deploy → health → smoke), rollback step, DB backup run with restore verification | Production release engineering                              |
| 9   | 10:30 | Intern 5   | `QA/milestone4/day6/final_regression_report.md` and Selenium screenshots                                                          | Full-system, cross-browser, performance, stability sign-off |
| 10  | 11:30 | Team lead  | Known limitations + next steps                                                                                                    | Free-tier cold starts, DB expiry handled by backups         |

## If something goes wrong

- **Page spins on first load** → service waking up; talk through the architecture for 30 s.
- **A service is down** → Render dashboard → service → Logs; worst case **Rollback** to the
  previous deploy (one click) and continue.
- **Backup plan** → run the same demo against the local Docker stack
  (`docker compose -f docker-compose.dev.yml up -d`), which uses the identical code.
