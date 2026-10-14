# Milestone 4 — Day 1 Summary (Intern 5: QA, DevOps & Release Engineering)

Date: 2026-10-04

## Checkpoints (SRS §11.5)

- [x] M4 plan written: `m4_test_deployment_plan.md` (test + deployment strategy, built from the
      M3 Deployment Readiness Checklist)
- [x] Defect tracker opened with M3 carry-overs: `defect_tracker.md`
- [ ] Deploy target confirmed by Team Lead (proposed: free-tier VM + Docker Compose)

## What was done (with evidence)

1. **Re-ran the baseline suite** on the current `Team-1` working tree:

   ```
   $ python -m pytest -q
   114 passed, 46 skipped, 5 xfailed, 194 warnings in 114.49s
   ```

   The 46 skips are live-stack tests (no running stack). The 5 xfails are known M1 contract defects.

2. **Re-checked the M3 readiness checklist** item by item against the code (plan §4):
   - DEF-M3-021 (hard-coded JWT key) is now fixed in source. The backend refuses to start without
     `JWT_SECRET_KEY`. It will be retested live.
   - Still not ready: CORS `*`, frontend URLs hard-coded to `127.0.0.1`, Tailwind CDN, no backups,
     no TLS.

3. **Checked the CI lint gate**, because the deploy stage depends on it:

   ```
   flake8: backend 230, analytics 42, QA 2  →  QA fixed to 0
   black --check: 66 files would be reformatted (QA: 1 → fixed)
   eslint: 93 problems (42 errors, 51 warnings)
   ```

   The QA-owned fix was `QA/milestone3/day6/regression_m1_m2.py`: Black formatting and one long comment.

4. **Chose the deployment approach**: one free-tier VM running Docker Compose, images in GHCR,
   immutable `sha-` tags, automatic rollback on a failed health check (plan §3).

## Blockers raised for stand-up

- **DEF-M4-001**: lint is red in the backend, analytics and frontend folders. Deploy cannot run
  until each owner cleans their folder.
- **DEF-M4-003**: project code is not committed/pushed, so GitHub has never run CI.
- **Decision needed (Team Lead)**: deploy target and cloud account, by Day 3.
- **DEF-M4-005**: Intern 4 needs a configurable API base URL before the frontend can go live.
