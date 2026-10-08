# TrafficVision AI — Milestone 3, Day 1
## Analytics Service & Alert-Trigger Planning
**Role:** Intern 2 — Data Engineering & Traffic Monitoring

---

## 1. Reviewing What Milestone 2 Already Gives Us

Good news — a lot of the groundwork already exists:

| M3 Requirement | Already covered by M2? |
|---|---|
| Trend analysis (`/analytics/trends`) | ✅ Mostly — `/traffic/aggregate` and `/traffic/features` already compute hourly/daily/weekday averages. This becomes a thin re-shaping of existing logic, not new work from scratch. |
| Historical reports (`/analytics/reports`) | ✅ Mostly — `/traffic/history` already returns raw data in a range; this just needs a CSV-formatted response instead of JSON. |
| Congestion heatmap (`/analytics/heatmap`) | ❌ New — needs a genuinely new grid structure: roads × time buckets, not just per-road averages. |
| Congestion-threshold breach feed | ❌ New — nothing in M1/M2 actively watches live data and reacts when it crosses a threshold. |

**Takeaway:** Milestone 3's Analytics Service is less "build everything from scratch" and more "reshape and extend what already works." The one genuinely new piece of engineering is the **heatmap grid** and the **threshold-watching feed**.

---

## 2. What's Genuinely New

### A. Heatmap Data Structure
Per the SRS contract:
```
GET /api/v1/analytics/heatmap?range={range}
→ { roads: [...], time_buckets: [...], values: [][] }
```
This is a **2D grid**: rows = roads, columns = time buckets (e.g., hours of day), cells = average congestion. Different shape than anything built so far — existing endpoints return flat lists or per-road objects, not a matrix.

### B. Congestion-Threshold Breach Feed
Per the SRS: "flags when live congestion crosses a threshold, exposing this as a feed that calls Intern 1's alert-creation endpoint."

**Design decision:** rather than hardcoding one global threshold, build a small `alert_thresholds` config table — so different roads (or road types) can have different sensitivity. A highway might reasonably run at 70% density without it being alarming; a narrow local road at 70% might be a real problem.

---

## 3. Schema Design Decision

### New table: `alert_thresholds`
Stores the congestion-density threshold above which a road should trigger a congestion alert — one row per road (or a default fallback).

### No new table needed for "alerts" themselves
Per the SRS, the `alerts` table itself is **owned by Intern 1** (Alert Service). My job is only to **detect** the breach and call **their** `POST /api/v1/alerts` endpoint — not to store alerts myself. This keeps ownership boundaries clean, matching the SRS's dependency matrix (Intern 1 depends on my feed, Day 2).

Since Intern 1's Alert Service isn't built in this solo workflow, I'll build my threshold-detection logic against the **documented contract shape** (`{ type, severity, road_id, message }`), the same way I built a minimal Gateway in Milestone 2 to prove Gateway integration solo.

---

## 4. Day 1 Checklist (from the SRS)
- [x] Analytics plan written (this document)
- [x] Schema/query design finalized (`alert_thresholds` table; heatmap grid shape decided)
- [x] Approach confirmed against the SRS contract (Section 7.1 for the alert call shape, Section 7.2 for my own endpoints)

---

## 5. Next Up: Day 2 Preview
Day 2 tasks (from the Milestone 3 SRS):
- Build the congestion-threshold monitoring logic
- Expose it as a feed that calls Intern 1's alert-creation endpoint (simulated/documented contract, since building solo)
