# Day 4 / 5 / 7 Re-verification (Milestone 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Date: 2026-09-13, after the backend (`Backend/` → flattened to `backend/`) and frontend (`Front-end (3)/`) redeliveries.

## Summary
The backend team fixed all three routing bugs (DEF-M2-002/003/004) and the frontend fixed the port mismatch (DEF-M2-015) — verified live, not just by reading code. That's real progress and closes out the API layer for Auth, Traffic Monitoring, and Route Analysis. But actually wiring the two together for real (which is what Day 5 requires) immediately surfaced **three new, more serious defects** (DEF-M2-016, 017, 018) that were invisible before, specifically *because* the app was always silently falling back to mock data. Fixing the obvious bugs exposed the ones underneath.

## Day 4 — API-level functional testing: mostly done
| Endpoint | Result |
|---|---|
| `POST /api/v1/auth/register` | ✅ 201, works (once a valid `gmail.com`/`yahoo.com`/`outlook.com`/`nitpy.ac.in` email + `admin`/`user`/`operator` role is used) |
| `POST /api/v1/auth/login` | ✅ 200, valid JWT returned |
| `GET /api/v1/auth/me` | ✅ 200 |
| `GET /api/v1/traffic/live`, `/road/{id}`, `/density` | ✅ all 200, correct contract paths |
| `GET /api/v1/route/optimize`, `/alternate` (authenticated) | ✅ 200, real OSM-resolved paths, sub-second after warm-up |
| `GET /api/v1/traffic/history`, `/aggregate`, `/road-condition/{id}` | ❌ 404 — still not merged from Intern 2's separate service |
| `GET /api/v1/predict/peak-hours`, `/delay` | ❌ 404 — still not built (Intern 3) |
| `/predict/congestion` contract | ❌ still POST with a 9-field body, not the documented `GET ?road_id=` (DEF-M2-005) |

**Verdict: Day 4 is now mostly complete for what exists.** What's tested, passes. What's missing is still missing — unchanged from before, still needs Intern 2's merge and Intern 3's remaining endpoints.

## Day 5 — Real integration cycle: blocked by 3 new defects, not the old ones
This is the first time this milestone the frontend and backend were both actually reachable at the same time, on the same port. Attempting the real end-to-end flow (register → login → use the app) surfaced:

- **DEF-M2-016 (High)**: The only signup flow the app has (Public role) sends a role value the backend's enum rejects. Self-registration is broken.
- **DEF-M2-017 (Critical)**: Logging in with a real account (`role: "user"`, since that's what's actually registerable) causes an **infinite redirect loop** — the tab never stops loading. Confirmed by Playwright's own navigation getting interrupted mid-flight, repeatedly. This is a hang, not a cosmetic bug.
- **DEF-M2-018 (Critical)**: Even after working around the login loop, the app's own request logic (`apiFetch`'s multi-host retry) aborts working requests to the real backend and falls back to mock data anyway — confirmed by comparing a raw authenticated `fetch()` (200, real data) against the same call made through the app's own code (`net::ERR_ABORTED`, falls through to a dead port, ends up on mock).

**Verdict: Day 5 cannot proceed.** Not because of the original routing bugs (those are fixed) — because fixing them exposed a working-as-designed mock-fallback system that's now actively hiding whether the rest of the app works. Nobody can reach real data through the UI right now, for reasons unrelated to the backend's correctness.

## Day 7 — Final sign-off: not possible yet
Blocked transitively by Day 5. Unchanged from before.

## Other findings this session
- The folder shared as "Intern 1's work" (`TrafficVision-AI 3/`) does not contain integration/merge work — it's a zip of `predict.py` + `model-v1.joblib`, byte-for-byte identical (barring a trailing newline) to what's already in `backend/app/routes/predict.py`. Whatever Intern 1 intended to share, this wasn't it.
- Intern 2 re-delivered as `Data/M2_Day7_Traffic_Monitoring_/` — same code, 35/35 tests still pass, one new doc file is empty (`M2_DAY7_FINAL_VALIDATION_AND_HANDOFF.md`). Still not merged into the shared backend.

## What's actually needed now, in priority order
1. **DEF-M2-017 (Critical)** — fix the role-vocabulary mismatch between backend (`admin`/`user`/`operator`) and frontend (`ADMIN`/`OPERATOR`/`PUBLIC`) so login doesn't hang. This blocks everything downstream.
2. **DEF-M2-018 (Critical)** — simplify `apiFetch` back to calling the real backend directly; the defensive multi-host retry logic is now actively breaking working requests.
3. **DEF-M2-016 (High)** — same role-vocabulary question, applied to signup.
4. Intern 1: merge Intern 2's historical data endpoints into `backend/app/`.
5. Intern 3: build `/predict/peak-hours`, `/predict/delay`, resolve the `/predict/congestion` contract mismatch (DEF-M2-005).

Once 1–3 land, Day 5 becomes possible for the first time this milestone, and Day 7 sign-off follows once 4–5 land too.

---

## Update — 2026-09-14: frontend redelivered, re-verified live

Frontend pushed fixes for DEF-M2-007/016/017/018. Re-tested every one live (real login form, real network requests, not code-reading):

| Defect | Result |
|---|---|
| DEF-M2-016 (signup role) | ✅ **Fixed** — register now returns 201, was 422 |
| DEF-M2-017 (login infinite loop) | ✅ **Fixed** — real `role: "user"` login redirects cleanly, page settles, no loop |
| DEF-M2-007 (stale route data) | ✅ **Fixed, confirmed for the first time** — ETA/distance genuinely changed on destination change (10min/8.4km → 9min/7.8km) |
| DEF-M2-018 (apiFetch retry logic) | ✅ Fixed — all 4 route requests now succeed at the network level (confirmed with request-level timing logs, not just app status) |

**But new issue found underneath (DEF-M2-019):** even with working network calls, the app still showed mock data. Root cause: a "stub backend detector" compares the backend's returned route coordinates against the hub coordinates to catch fake/hardcoded responses — but it never swaps coordinate order. Hub coords are `[lat, lng]`; the backend's GeoJSON-style path is `[lng, lat]`. The check compares longitude against latitude as if they were the same axis, always computes a nonsense distance, always trips the "this looks fake" threshold, and always falls back to mock even on genuine data. Sent to frontend intern.

**Separately, a real security finding (DEF-M2-020, Critical):** while doing RBAC re-verification, found that `POST /api/v1/auth/register` accepts `role: "admin"` or `"operator"` from any unauthenticated caller — confirmed by registering a throwaway admin account via raw `curl` (no frontend involved) and logging in with it; the JWT genuinely carries `role: admin`. Anyone who can reach the API can grant themselves admin access. This is backend-side, predates the frontend's changes entirely, and is now the top-priority item — sent to Intern 3, ranked above the historical-data merge.

### Updated Day 5 status
Still blocked, but for narrower reasons now — login/signup/route-recalc all genuinely work. What's left: DEF-M2-019 (so real data actually displays) and DEF-M2-020 (so RBAC has an actual boundary to test) must land before a real integration cycle is meaningful.
