# Intern 5 — QA, DevOps & Release Engineering (Vaishnavi Titare)

QA work for TrafficVision AI, Milestones 1–4.

**Live system:** https://trafficvision-ai-i8e2.onrender.com · Frontend: https://trafficvision-ai.vercel.app/Login
**Final status (M4 Day 6):** ✅ STABLE — approved for final demo (smoke 32/32, full system 65/65, Selenium 67/67, stability 100%)

## In this folder

| Folder | Contents |
| --- | --- |
| [`milestone1/`](milestone1) | M1 QA: Day 1–7 test plans, API/UI tests, regression, code quality, test scripts |
| [`milestone2/`](milestone2) | M2 QA, DevOps & release: test reports, screenshots, Milestone2_QA_Report.pdf |
| [`milestone3/`](milestone3) | M3 QA: integration cycles, alert delivery checks, retests, deployment readiness checklist |
| [`milestone4/`](milestone4) | M4 live deployment QA, Day 1–7: defect tracker, smoke, full system, Selenium, performance, final regression report |
| [`test-cases/`](test-cases) | Auth and traffic-monitoring test cases, Day 4 execution report, screenshots |
| [`tools/`](tools) | QA helper scripts |

## DevOps work at the repository root

These files are also by Intern 5. They stay at the root because GitHub Actions, Docker and the
lint/test tools only read them from there.

| What | Files |
| --- | --- |
| CI/CD pipelines | [`.github/workflows/`](../.github/workflows): `ci.yml` (lint → test → build → deploy → verify → smoke), `live-qa.yml`, `db-backup.yml`; [defect issue template](../.github/ISSUE_TEMPLATE) |
| Deployment | [`render.yaml`](../render.yaml), [`Dockerfile`](../Dockerfile), [`docker-compose.yml`](../docker-compose.yml), [`docker-compose.dev.yml`](../docker-compose.dev.yml), [`docker-compose.prod.yml`](../docker-compose.prod.yml), [`.env.dev.example`](../.env.dev.example), [`.env.prod.example`](../.env.prod.example) |
| Quality gates | [`.flake8`](../.flake8), [`.eslintrc.json`](../.eslintrc.json), [`.prettierrc.json`](../.prettierrc.json), [`.prettierignore`](../.prettierignore), [`pyproject.toml`](../pyproject.toml), [`package.json`](../package.json), [`conftest.py`](../conftest.py), [`tests/`](../tests) |
| Documentation | [`docs/`](../docs): setup guide, test plan, quality gates, PR checklist, bug board; [`docs/final/`](../docs/final): architecture, API reference, deployment guide, demo script |

The same QA reports are kept in [`QA/`](../QA) at the root, which the CI pipeline runs from.
