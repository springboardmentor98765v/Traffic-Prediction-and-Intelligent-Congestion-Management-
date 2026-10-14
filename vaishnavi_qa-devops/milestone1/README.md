# Milestone 1 QA Deliverables: Intern 5 (QA, DevOps & Release Engineering)

Everything Intern 5 owes for Milestone 1 (SRS sections 10.5, 11.5 and 13), organized by day.
**Verdict:** conditional sign-off. See `day7/m1_qa_signoff_report.md`.

| Day | SRS task                                                                     | Deliverables                                                                                                                                                                                                           |
| --- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Code-quality tooling, PR checklist, branch policy, test plan, defect tracker | [`m1_test_plan.md`](day1/m1_test_plan.md), [`m1_test_scope.md`](day1/m1_test_scope.md), [`defect_tracker.md`](day1/defect_tracker.md), [`quality_gates_and_branch_policy.md`](day1/quality_gates_and_branch_policy.md) |
| 2   | CI (lint + build, no deploy), `docker-compose.dev.yml`                       | [`day2_ci_and_local_env.md`](day2/day2_ci_and_local_env.md), `compose_services.txt`                                                                                                                                    |
| 3   | Test cases for Auth/RBAC and Monitoring, automated suite skeleton            | [`m1_test_cases.md`](day3/m1_test_cases.md), [`tests/`](tests/)                                                                                                                                                        |
| 4   | Execute functional tests, log defects, CI runs tests                         | [`day4_test_execution_report.md`](day4/day4_test_execution_report.md), `day4_pytest_output.txt`                                                                                                                        |
| 5   | Full integration cycle in compose, RBAC end to end                           | [`day5_integration_test_report.md`](day5/day5_integration_test_report.md), [`m1_live_stack_check.py`](day5/m1_live_stack_check.py), `ui/` (browser evidence)                                                           |
| 6   | Regression, coverage, static code-quality report                             | [`m1_day6_regression_report.md`](day6/m1_day6_regression_report.md), [`m1_day6_code_quality_report.md`](day6/m1_day6_code_quality_report.md)                                                                           |
| 7   | Final validation, QA sign-off, test summary                                  | [`m1_qa_signoff_report.md`](day7/m1_qa_signoff_report.md), [`m1_test_summary.md`](day7/m1_test_summary.md), `m1_pytest_junit.xml`                                                                                      |

## How to re-run

```bash
# Automated suite (no Docker needed; also runs in CI through pyproject testpaths)
python -m pytest -v QA/milestone1/tests

# Live stack
docker compose -f docker-compose.dev.yml up -d --build
python QA/milestone1/day5/m1_live_stack_check.py
# Optional RBAC allow path:
OPERATOR_EMAIL=... OPERATOR_PASSWORD=... python QA/milestone1/day5/m1_live_stack_check.py

# Browser E2E (Playwright + Edge), evidence written to day5/ui
PYTHONPATH=QA/milestone3/tests M3_OUT_DIR=QA/milestone1/day5/ui python QA/milestone3/day5/frontend_e2e.py
```

## Test suite layout (`tests/`)

| File                              | Covers                                              |
| --------------------------------- | --------------------------------------------------- |
| `conftest.py`, `m1_helpers.py`    | TestClient, Public / Operator / Admin fixtures      |
| `test_m1_auth.py`                 | SRS 7.1 Auth (TC-AUTH-01..21)                       |
| `test_m1_rbac.py`                 | FR-02 RBAC (TC-RBAC-01..10)                         |
| `test_m1_traffic.py`              | SRS 7.2 Monitoring (TC-TRF-01..09)                  |
| `test_m1_prediction.py`           | SRS 7.3 Prediction stub (TC-PRED-01..08)            |
| `test_m1_gateway_and_frontend.py` | Gateway contract and frontend wiring (TC-GW, TC-UI) |

Open defects are pinned with `@pytest.mark.xfail(strict=True, reason="DEF-M1-xxx")`. When a fix lands, the test reports XPASS and fails the run, so the marker must be removed.
