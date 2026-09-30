# Milestone 3 — Day 1 Summary (Intern 5: QA, DevOps & Release Engineering)

Date: 2026-09-24

## Checkpoints (per SRS Section 11.5)

- [x] Milestone 3 test scope written down — `milestone3_test_scope.md`
- [x] Bug/defect tracker updated — `defect_tracker.md` (2 M2 defects closed on re-check, 3 still
      open carried forward, 3 new Day 1 defects logged)
- [x] Plan shared with the team — this summary + the three docs above, committed to the shared repo
      under `QA/milestone3/day1/`

## What was actually done (with evidence)

1. **Reviewed the Milestone 1 & 2 QA setup.** Re-ran the existing automated suite on a clean
   checkout of `Team-1`:

   ```
   $ python -m pytest -q
   3 failed, 1 passed, 152 warnings in 12.71s
   ```

   Root-caused all 3 failures — 2 are a stale test file (`tests/test_day4_api.py`, pre-M2-fix
   routes, logged as DEF-M3-001), 1 is expected outside Docker (needs the `postgres` Compose
   hostname, logged as DEF-M3-002). No new regressions found in M1/M2 functionality itself.

2. **Re-verified 5 carried-forward Milestone 2 defects**: 2 confirmed fixed and closed
   (DEF-M2-006 auth import, DEF-M2-013 plaintext `.env` credentials — root `.gitignore` now
   covers them), 3 confirmed still open (DEF-M2-008 unpinned scikit-learn, DEF-M2-011 dead
   auth-service code, DEF-M2-012 ESLint false positive — not re-run this session).

3. **Validated the local Docker setup is still a usable starting point** for Day 2's compose
   extension:

   ```
   $ docker compose -f docker-compose.dev.yml config -q
   (warning: obsolete `version` key — DEF-M3-003, Low)
   ```

4. **Defined the Milestone 3 test scope** covering Alert Service, Analytics Service, AI Insights
   (anomaly detection + recommendations), and notification delivery — see
   `milestone3_test_scope.md`.

5. **Checked for existing Milestone 3 feature code** across every branch in the repo (`main`,
   `Team-1..4`, and all individual intern branches) — confirmed none exists yet. `Front-end/Front-end/Alerts.html`
   is present but is static markup with no live API calls (`fetch(...)`) wired in. This means Day 2's
   docker-compose extension and Day 3+'s test execution are currently blocked on Intern 1
   (Alert Service) and Intern 2 (Analytics Service) landing their skeletons/contracts, per the
   Day 2 (EOD) contract-freeze checkpoint.

## Blockers / risks flagged to the team

- **No Alert/Analytics/AI Insights code exists yet anywhere in the repo.** The Day 2 contract
  freeze and Day 3 test-case work depend on Intern 1 & 2 delivering API contracts on time —
  currently the critical path for the whole milestone.
- DEF-M3-001/002 should be fixed or explicitly marked environment-dependent before the Day 6
  regression pass, so a clean `pytest -q` run is a meaningful signal at sign-off time.
