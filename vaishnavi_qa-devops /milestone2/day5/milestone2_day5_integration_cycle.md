# Day 5 — Full Local Integration Test Cycle (Milestone 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Per SRS Section 10.5 Day 5: "Run a full local integration test cycle covering Auth + Monitoring + Prediction + Route Analysis + Frontend together; verify maps integration doesn't break other flows; re-verify RBAC on the new endpoints."

**Note on organization:** same gap as Day 4 — this work happened but got recorded inside the Day 7 doc instead of its own file. Consolidating here.

## Attempt 1 (2026-09-13) — blocked immediately
First time backend and frontend were both reachable on the same port. Attempting the real login → app flow surfaced three defects that made integration testing impossible:
- DEF-M2-016 — signup rejected (role enum mismatch)
- DEF-M2-017 — login caused an infinite redirect loop (tab freeze)
- DEF-M2-018 — even working around the loop, the app's own request logic aborted working calls and silently used mock data

**Verdict: could not proceed.** Full detail in `QA/milestone2/day7/milestone2_day4_5_7_reverification.md`.

## Attempt 2 (2026-09-14) — frontend fixes landed, deeper issue found
Re-tested live: DEF-M2-016, 017, and the retry-logic half of 018 all confirmed fixed. Route recalculation (DEF-M2-007) confirmed working for the first time. But a new issue (DEF-M2-019, lat/lng coordinate order swapped in a stub-detection check) meant the app still never displayed real backend data even though the network calls were succeeding.

Separately, doing the RBAC re-check this day required found **DEF-M2-020 (Critical security)**: the registration endpoint let anyone self-assign `admin` or `operator` with no authorization at all — confirmed with a real JWT containing `role: admin` minted from an anonymous request. This meant RBAC testing was pointless until fixed — the role boundary didn't actually exist.

**Verdict: still could not proceed** — closer, but blocked by DEF-M2-019 and DEF-M2-020.

## Attempt 3 (2026-09-15) — backend now fully verified live; blocked on one remaining frontend fix
Backend redelivered, rebuilt, and re-verified live end-to-end (Docker was briefly down mid-session, restarted and retested):
- **DEF-M2-020 confirmed fixed live** — registered with `role: "admin"` in the request (still 201), then logged in and decoded the JWT: `role` comes back `PUBLIC`, not admin. Server-side hardcoding closes the privilege-escalation hole for real.
- **Historical data merge confirmed fixed live** — `/traffic/history`, `/traffic/aggregate`, `/traffic/road-condition/{id}` all return 200 with real data.
- **Route analysis confirmed still working** — `/route/optimize` returns 200 with real OSM path data, authenticated.
- No regression on DEF-M2-002/003/004.

**Then checked the frontend** (unchanged folder, no new delivery since 2026-09-14): DEF-M2-019 (lat/lng coordinate swap in the stub-detection check) is still present in the code. Live-tested the full flow — real login, navigate to Route Analysis — and confirmed: `data_source_badge` still reads **"MOCK DATA"**, even though every backend call it depends on now genuinely works.

**Verdict: backend side of Day 5 is done. Frontend has exactly one remaining blocker (DEF-M2-019).** Once that lands, this should be the first attempt that actually passes.

## Attempt 4 (2026-09-15, same day) — DEF-M2-019 fixed, real data confirmed end-to-end

Frontend redelivered (`Front-end/Front-end/`). `ptToArr` now correctly swaps to `[pt[1], pt[0]]`. Live-tested the full flow again — real login, Route Analysis page:

- **`data_source_badge` reads `● LIVE API`** — not mock, for the first time this milestone.
- ETA/distance show realistic decimal values (`11.31 mins`, `8.5 km`), not the old round mock numbers.
- Changing destination correctly re-fetches and updates (`10.6 mins`, `9 km`) — confirms DEF-M2-007 (route recalculation) is also holding up under real data, not just mock.

**All 4 frontend integration blockers (DEF-M2-016/017/018/019) are now fixed and verified live.** Backend side (DEF-M2-002/003/004/005-partial/020, historical data merge) is also verified live.

### What's left before Day 5 can be marked fully complete
- `/predict/peak-hours` and `/predict/delay` still don't exist (Intern 1) — Prediction Service coverage is incomplete, so the integration cycle can't exercise the full FR-02/03/04 scope yet.
- `/predict/congestion` contract mismatch (DEF-M2-005) still open — same owner.
- A real RBAC pass across admin/operator/public roles against the now-working, now-secured role boundary hasn't been done yet (previous RBAC checks were either pre-DEF-M2-020-fix or against mock data).
- Maps integration / other flows (Live Traffic, dashboards) haven't been re-confirmed against real data yet — everything tested so far has been Route Analysis specifically.

## Overall Status
Massive progress today: every frontend and backend blocker that QA could independently verify is now fixed and confirmed live, not just by reading code. What's left is narrow and specific — Prediction Service completion from Intern 1, and a final RBAC + full-app regression pass once that lands.

## What "full integration cycle" actually requires before it can be marked complete
1. DEF-M2-019 fixed (frontend) — so real backend data actually displays instead of silently falling back to mock
2. DEF-M2-020 fixed (backend) — confirmed via code review, pending live re-test
3. Real RBAC re-check across all 3 roles (admin/operator/public) against the now-meaningful role boundary
4. Maps integration confirmed not to break other flows (Live Traffic, dashboards) under real data
5. `/predict/peak-hours` and `/predict/delay` still don't exist (Intern 1) — full Prediction Service coverage isn't possible until these land, though the core integration cycle doesn't strictly require every endpoint to exist to be meaningful

## Overall Status
Not yet complete. Three attempts so far, each one closer than the last — this is normal for an integration day that depends on multiple other people's fixes landing together, not a QA delay. Once Docker is back up, re-verifying attempt 3's fixes live is the immediate next step.
