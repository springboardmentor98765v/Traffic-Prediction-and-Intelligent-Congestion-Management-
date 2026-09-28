# TrafficVision AI — Milestone 2, Day 1
## Data Plan & Historical Storage Design
**Role:** Intern 2 — Data Engineering & Traffic Monitoring

---

## 1. Reviewing What Milestone 1 Already Gives Us

Good news: `traffic_readings` (built Day 1 of Milestone 1) is **already a time-series table** — every row has a `recorded_at` timestamp, and it's been continuously growing since Milestone 1's ingestion script has been running. This means we don't need to build historical storage from scratch — we need to:

1. Make sure it can be **queried efficiently** over time ranges (not just "latest")
2. Add **aggregation** support (hourly/daily averages) for Intern 3's model features
3. Add a new **road_conditions** table (closures, construction, hazards) — genuinely new for M2
4. Decide: do we need TimescaleDB, or is plain indexed PostgreSQL enough?

---

## 2. Decision: TimescaleDB vs Plain Indexed PostgreSQL

The SRS allows either. Here's the trade-off:

| Option | Pros | Cons |
|---|---|---|
| **TimescaleDB extension** | Built for time-series at scale; automatic partitioning ("hypertables"); very fast time-range + aggregate queries | Extra install step; adds complexity for a 7-day sprint scope |
| **Plain PostgreSQL + good indexing** | Already running; zero new install; `traffic_readings` already has a working index from Milestone 1 | Won't scale as gracefully into millions of rows long-term |

**Decision for Milestone 2:** Start with **plain indexed PostgreSQL** — our current data volume (5 roads × readings every 5 seconds) doesn't yet justify TimescaleDB's complexity, and the SRS explicitly allows this as a valid free option. This is documented as a decision, not an oversight, in case a mentor asks why TimescaleDB wasn't used.

**If data volume grows significantly in a later milestone**, TimescaleDB can be added later without changing the API contract — the `/traffic/history` and `/traffic/aggregate` endpoints would return the same shape either way.

---

## 3. Schema Additions for Milestone 2

### New table: `road_conditions`
Tracks closures, construction, and hazards — genuinely new data that didn't exist in Milestone 1.

### New index: optimized for time-range queries
Milestone 1's `idx_traffic_road_time` was built for "give me the latest reading" (ORDER BY ... DESC LIMIT 1). Milestone 2 needs **range queries** ("give me everything between two timestamps") — the same index actually already supports this well, but we'll verify with EXPLAIN ANALYZE once the history endpoint is built (Day 3).

---

## 4. What Gets Provided to Intern 3 (AI/ML)

Per the Dependency Matrix (SRS Section 8): Intern 3 needs the historical data API + aggregated metrics by **Day 2**. That means:
- Day 1 (today): schema design + plan
- Day 2: actual time-series storage decision implemented + simulated multi-week historical dataset generated

---

## 5. Day 1 Checklist (from the SRS)
- [x] Historical data plan written (this document)
- [x] Table/storage design finalized (road_conditions table + reuse of traffic_readings)
- [x] Schema approach confirmed (documented decision: plain indexed PostgreSQL, not TimescaleDB, for this milestone's scope)
