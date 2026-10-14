# Intern 5 — QA, DevOps & Release Engineering (Vaishnavi Titare)

All work pushed by Intern 5 for TrafficVision AI, in one place.

**Live system:** https://trafficvision-ai-i8e2.onrender.com · Frontend: https://trafficvision-ai.vercel.app/Login
**Final status (M4 Day 6):** ✅ STABLE — approved for final demo (smoke 32/32, full system 65/65, Selenium 67/67, stability 100%)

## Folder structure

| Folder | Contents |
| --- | --- |
| `milestone1/` | M1 QA: Day 1–7 test plans, API/UI tests, regression, code quality, test scripts |
| `milestone2/` | M2 QA, DevOps & release: test reports, screenshots, Milestone2_QA_Report.pdf |
| `milestone3/` | M3 QA: integration cycles, alert delivery checks, retests, deployment readiness checklist |
| `milestone4/` | M4 live deployment QA: Day 1–7 (defect tracker, smoke, full system, Selenium, performance, final regression report) |
| `test-cases/` | Auth and traffic-monitoring test cases, Day 4 execution report, screenshots |
| `docs/` | Setup guide, test plan, quality gates, PR checklist, bug board; `docs/final/` architecture, API reference, deployment guide, demo script |
| `devops/ci-cd/` | GitHub Actions workflows (CI, live QA, DB backup) and defect issue template |
| `devops/deployment/` | Render Blueprint, Dockerfile, docker-compose (dev/prod), example env files (no secrets) |
| `devops/quality-gates/` | Lint/format/test config: flake8, ESLint, Prettier, pyproject, conftest |
| `devops/tests/` | API tests |
| `tools/` | QA helper scripts |

## Notes

- The files in `devops/` are reference copies. The working copies stay at the repository root
  (`.github/`, `render.yaml`, `docker-compose*.yml`, …) because GitHub Actions and Docker only read them from there.
- `QA/` at the repository root holds the same QA reports; this folder is the Intern 5 submission view.
- Application code (backend, analytics, AI engine, frontend) belongs to Interns 1–4 and is not copied here.
