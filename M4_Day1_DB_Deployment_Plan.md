# TrafficVision AI — Milestone 4, Day 1
## Production Database Deployment Plan
**Role:** Intern 2 — Data Engineering & Traffic Monitoring

---

## 1. What's Different About This Milestone

Milestones 1–3 only ever ran against a **local** PostgreSQL instance (on your own machine, via Docker or a native install). Milestone 4's job is to take that same schema and data and put it on a **real, publicly-reachable cloud database** — the only milestone where this happens. Per the SRS, no new API endpoints are built this milestone; the contract is already frozen. The work here is entirely about *where* the data lives and *how reliably* it's protected, not what it returns.

---

## 2. Choosing a Free-Tier Cloud Database

The SRS's tooling policy requires free-tier only. Options for a managed PostgreSQL instance:

| Provider | Free Tier | Notes |
|---|---|---|
| **Render** | Free PostgreSQL (90-day limit, then needs recreation) | Easiest setup, good for a demo project |
| **Railway** | Free tier with usage credits | Simple deploy, generous limits for small projects |
| **Supabase** | Free PostgreSQL + extras (not needed here) | Good if extra tooling (auth, storage) were ever wanted |
| **Neon** | Free serverless PostgreSQL | Scales to zero when idle — good for a project with bursty usage |

**Decision for this milestone:** **Render** — free tier covers this project's scope fully, simplest to set up and monitor via its own dashboard without additional tooling, and avoids any surprise cost since it has zero paid-tier resources. Documented here as a deliberate choice (matching the project's established pattern of writing down *why* a decision was made, not just what was chosen).

---

## 3. Migration Strategy

### Step 1: Export the local database
```bash
pg_dump -U postgres -d trafficvision -F c -f trafficvision_backup.dump
```
`-F c` uses PostgreSQL's custom compressed format — smaller file, and restorable with `pg_restore` even if the exact schema order changes.

### Step 2: Restore into the new cloud database
```bash
pg_restore -h <cloud-host> -U <cloud-user> -d trafficvision -1 trafficvision_backup.dump
```
`-1` wraps the whole restore in a single transaction — if anything fails partway, the entire restore rolls back cleanly instead of leaving a half-migrated database.

### Step 3: Verify row counts match before considering migration complete
```sql
SELECT COUNT(*) FROM traffic_readings;
SELECT COUNT(*) FROM roads;
SELECT COUNT(*) FROM alert_thresholds;
SELECT COUNT(*) FROM road_conditions;
```
Run this on BOTH local and cloud databases, compare directly. This is the "data parity" check the SRS calls out explicitly for Day 4 — starting the habit on Day 1 by defining exactly what will be compared later.

---

## 4. Backup Strategy

Per the SRS (owner: Intern 2): "automated daily backup job" + a tested restore process.

**Plan:**
- Daily automated `pg_dump` via a scheduled job (cron, or the cloud provider's built-in backup feature if available on the free tier)
- Retain the last 7 days of backups (older ones can be deleted — a week is enough buffer for this project's scope)
- **Critically: actually test a restore**, not just trust that backups exist. An untested backup is not a real backup — Day 3 will do this explicitly.

---

## 5. Environment Variables Needed

Per the SRS's Production Config section (owned by Intern 1, but my database needs to supply its piece):
```
DB_URL=postgresql://<user>:<password>@<cloud-host>:5432/trafficvision
```
This replaces the hardcoded `DB_CONFIG` dictionary used throughout Milestones 1–3's scripts — a necessary change for Day 2, since committing real credentials into scripts (even private ones) is bad practice once a real cloud database is involved.

---

## 6. Day 1 Checklist (from the SRS)
- [x] DB deployment plan written (this document)
- [x] Cloud provider chosen and justified
- [x] Migration approach defined (pg_dump / pg_restore)
- [x] Backup strategy outlined
- [x] Environment variable contract identified for Intern 1

---

## 7. Next Up: Day 2 Preview
Day 2 tasks (from the Milestone 4 SRS):
- Actually set up the live production database
- Migrate the schema and all existing data into it
- Depends on: Intern 1's env var contract being finalized
