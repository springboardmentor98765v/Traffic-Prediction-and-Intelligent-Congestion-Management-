# TrafficVision AI — Milestone 1 Demo Walkthrough & Rehearsal Guide

## Objective
Demonstrate complete Milestone 1 deliverables across Days 1 through 7 for the TrafficVision AI platform.

---

## 1. Project Initialization & Wireframes (Days 1 & 2)
1. Show repository structure:
   - Next.js 15 App Router + Tailwind CSS 4 setup.
   - Comprehensive documentation in `/docs`: `wireframes.md`, `api-contracts.md`, `frontend-notes.md`.
2. Highlight the reusable UI component library:
   - `Navbar.tsx`: Live API vs Mock simulation indicator toggle, responsive drawer, role badge.
   - `Sidebar.tsx`: Persistent navigation with active route highlights.
   - `Card.tsx`, `Badge.tsx`, `ErrorMessage.tsx`, and `RoadDetailModal.tsx`.

---

## 2. Authentication & RBAC Verification (Day 3 & Day 5)
1. Open `http://localhost:3000/login`.
2. Demonstrate **1-Click Quick Demo Login**:
   - Click **"⚡ Demo Admin"** — Instant login with `admin` claims. Note the Purple "ADMIN" badge in top-right.
   - Click **Logout**.
   - Click **"⚡ Demo Operator"** — Instant login with `operator` claims. Note Amber "OPERATOR" badge.
   - Demonstrate manual input validation by submitting an invalid email to trigger validation feedback.

---

## 3. Live Traffic Dashboard (Day 4)
1. Navigate to `/dashboard`:
   - Inspect the **4 KPI Cards**:
     - City Congestion Index with live trend.
     - Monitored Corridors (5 active).
     - Average Network Speed (km/h).
     - Active Bottlenecks & Critical Incidents.
   - Inspect the **Monitored Corridors Table**:
     - MG Road (R001), Ring Road (R002), Station Road (R003), Airport Road (R004), Civil Lines (R005).
     - Observe live polling: values update dynamically every 5 seconds.
   - Click any road row (e.g. **MG Road**):
     - Opens the **Road Detail Telemetry Modal**.
     - View 24-hour historical density sparkline/chart and AI Congestion Prediction confidence score.

---

## 4. Interactive Live Traffic Map (Day 5)
1. Navigate to `/live-map`:
   - Observe the dark-mode cyber vector road network topology.
   - Watch animated flow pulses indicating traffic velocity along each arterial corridor.
   - Test the **Filter by Status** buttons (`All`, `High`, `Medium`, `Low`).
   - Click road pins to view real-time popover telemetry cards with vehicle volume and congestion forecast.

---

## 5. Alerts & Incident Management (Day 6)
1. Navigate to `/alerts`:
   - Review the real-time queue of bottleneck alerts.
   - Filter by severity: `Critical`, `Warning`, `Advisory`.
   - In Operator/Admin role, click **"Acknowledge"** or **"Resolve"** to demonstrate instant state changes and toast alerts.
   - Demonstrate **"Broadcast Incident"** dialog.

---

## 6. Traffic Analytics & AI Forecasting (Day 7)
1. Navigate to `/analytics`:
   - Inspect the 24-hour congestion pattern showing morning rush (08:00-10:00) and evening peak (17:00-20:00).
   - Review the arterial road throughput comparison matrix and emission reduction index.

---

## 7. Dual Live/Mock Backend Resilience
1. In the top navbar, observe the connection indicator:
   - If FastAPI server is running on `localhost:8000`, the indicator shows `Live Backend 🟢`.
   - If FastAPI server is offline, the indicator smoothly falls back to `Simulation Mode 🟡` with zero UI disruption or broken states.
