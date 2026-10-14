# TrafficVision AI — Milestone 3 Frontend Module Notes & Demo Rehearsal

## Executive Summary
Milestone 3 completes the transformation of TrafficVision AI into an enterprise-grade intelligent traffic command and congestion mitigation ecosystem. The frontend delivers four core capability pillars:
1. **Notification Bell & Triage Alerts Flyout**: Omnipresent top-bar alert drawer connected to Intern 1's real alert delivery endpoints (`GET /alerts/my`, `POST /alerts/{id}/read`).
2. **Analytics Dashboard**: Longitudinal multi-metric SVG trend charts consuming Intern 2's `/analytics/trends` endpoint across 24h, 7d, and 30d temporal windows.
3. **7×24 Diurnal Congestion Heatmap Matrix**: Comprehensive 168-cell matrix mapping temporal density profiles consuming Intern 2's `/analytics/heatmap` endpoint with corridor-level inspection.
4. **AI Decision Recommendations Panel & Impact Simulation**: Algorithmic decision support consuming Intern 3's `/ai/recommendations` endpoint with live Before vs After impact comparison modals.
5. **Historical Report Export Center**: Multi-format report generation (CSV, JSON, and Printable Executive HTML/PDF) with temporal and corridor filters.

---

## Technical Architecture & Component Hierarchy

```text
app/
├── components/
│   ├── Navbar.tsx                   # Embeds NotificationBell & RBAC controls
│   ├── NotificationBell.tsx         # [NEW M3] Bell button + flyout drawer
│   ├── TrendChart.tsx               # [NEW M3] Interactive SVG time-series visualizer
│   ├── CongestionHeatmap.tsx        # [NEW M3] 7x24 grid density heatmap matrix
│   ├── AIRecommendationsPanel.tsx   # [NEW M3] Decision support deck + simulation modal
│   ├── ReportExportModal.tsx        # [NEW M3] Multi-format export dialog (CSV/JSON/HTML)
│   ├── Badge.tsx                    # Shared severity & status pills
│   ├── Card.tsx                     # Glassmorphic cyber container
│   ├── Layout.tsx                   # Base page scaffold
│   ├── LeafletMap.tsx               # Leaflet geographic map
│   └── RoadDetailModal.tsx          # Corridor historical modal
├── lib/
│   ├── api.ts                       # Integrated client: /alerts/my, /analytics/*, /ai/*
│   ├── auth-context.tsx             # JWT session & RBAC role switcher
│   └── traffic-context.tsx          # Real-time polling & recommendation dispatcher
└── analytics/page.tsx               # [NEW M3] Upgraded Analytics Intelligence Command Center
```

---

## Inter-Team Contract Wiring Matrix

| Component | Target Endpoint | Backend Owner | Fallback Simulation Behavior |
|---|---|---|---|
| **Notification Bell** | `GET /api/v1/alerts/my` | Intern 1 | Simulated active alerts with critical ping indicator |
| **Alert Triage Action** | `POST /api/v1/alerts/{id}/read` | Intern 1 | Marks status as acknowledged/resolved; decrements counter |
| **Trend Charts** | `GET /api/v1/analytics/trends` | Intern 2 | Generates 24h diurnal curve, 7d longitudinal, and 30d capacity points |
| **Congestion Heatmap** | `GET /api/v1/analytics/heatmap` | Intern 2 | Computes 168 cells with weekday rush vs weekend patterns |
| **AI Recommendations** | `GET /api/v1/ai/recommendations` | Intern 3 | Realistic strategies for signal timing, detours, and ramp metering |
| **Apply AI Action** | `POST /api/v1/ai/recommendations/{id}/apply` | Intern 3 | Sets status to applied; lowers target corridor density by 15% |
| **Report Export** | Client-side Blob generator | Frontend / Intern 2 | Downloads formatted `.csv`, `.json`, or opens printable `.html` |

---

## Rehearsed Step-by-Step Demo Flow

Follow this exact sequence for the Milestone 3 final presentation:

### Step 1: Authentication & RBAC Session
- **URL**: `http://localhost:3000/login`
- **Action**: Click the **"Operator Demo"** or **"Admin Demo"** quick-fill button.
- **Talking Point**: *"TrafficVision AI supports role-based access control. Logging in as an Operator provides access to live incident dispatch and algorithmic recommendation tools."*

### Step 2: Situational Command Center & Notification Bell
- **URL**: `http://localhost:3000/dashboard`
- **Action**:
  1. Point out the top 4 KPI cards (City Congestion Index, Monitored Corridors, Flow Velocity).
  2. Direct attention to the **Notification Bell** in the top-right header displaying the active badge counter (`3`).
  3. Click the bell icon to reveal the floating Alerts flyout.
  4. Switch between the **"Critical"**, **"Warning"**, and **"All"** filter tabs.
  5. Click **"Acknowledge"** on an alert; show how the unread count instantly decrements.
- **Talking Point**: *"The Notification Bell provides omnipresent situational awareness across all pages, allowing operators to triage incoming bottlenecks without leaving their current workflow."*

### Step 3: Route Analysis & Geo Avoidance
- **URL**: `http://localhost:3000/route-analysis`
- **Action**: Select Origin (Station Road Hub) and Destination (Airport Terminal). Review the recommended bypass vs alternate routes rendered on the dark-mode Leaflet map.
- **Talking Point**: *"Route Optimization combines real-time arterial densities with predictive AI to steer traffic away from choke points."*

### Step 4: Analytics Dashboard (Trend Charts + 7×24 Heatmap)
- **URL**: `http://localhost:3000/analytics`
- **Action**:
  1. Review the 4 high-level intelligence metrics (Prediction Precision 88.4%, Lead Time 22 min, Carbon Offset -14.2%, Active Interventions).
  2. On the **Traffic Density & Flow Velocity Trends** chart:
     - Toggle between **"24h"**, **"7d"**, and **"30d"**.
     - Switch from **"Citywide Average"** to **"Corridor Comparison"**.
     - Toggle individual corridor lines on and off using the corridor pills.
     - Move the cursor over the chart to demonstrate the interactive vertical crosshair and floating tooltip.
  3. Scroll to the **7×24 Diurnal Congestion Heatmap Matrix**:
     - Change the **Corridor Scope** dropdown to inspect "Station Road" vs "Citywide Network".
     - Hover over high-density cells (e.g., Friday 18:00) to show the inspection strip displaying exact density %, flow speed in km/h, and bottleneck risk index.
- **Talking Point**: *"The 7×24 heatmap exposes recurrent systemic gridlock windows, revealing that Station Road bottlenecks crest consistently on Friday evenings."*

### Step 5: AI Decision Recommendations & Algorithmic Simulation
- **URL**: `http://localhost:3000/analytics` or `/dashboard`
- **Action**:
  1. Locate the **AI Recommendations Panel**.
  2. Point out recommendation cards (e.g., *Station Road Ingress Green Phase Extension* with -34% delay reduction).
  3. Click **"Simulate Impact"** on the recommendation card.
  4. Walk through the Before vs After simulation comparison modal showing quantified bars for Transit Delay, Density %, and Queue Spillback Length (850m &rarr; 320m).
  5. Click **"⚡ Apply Optimization Now"**.
  6. Point out the success toast notification, the status updating to **"Applied"**, and the corresponding reduction in Station Road's live congestion density.
- **Talking Point**: *"Rather than guessing, operators can simulate the exact queue reduction before applying automated signal timing or detour broadcasts with a single click."*

### Step 6: Historical Report Download
- **URL**: `http://localhost:3000/analytics` or `/dashboard`
- **Action**:
  1. Click **"Download Historical Report"** in the top action bar.
  2. Select temporal range ("Last 24 Hours"), corridor scope, and dataset checkboxes.
  3. Click **"Download CSV"** to demonstrate spreadsheet download.
  4. Click **"Executive Report"** to open the print-ready executive summary document with formatted tables and KPIs.
- **Talking Point**: *"Auditing and compliance reports can be exported on demand in CSV for data analysts or printable executive summaries for city administrators."*

---

## QA & Stability Checklist (Day 6 Integration Verification)

- [x] **Zero TypeScript Errors**: Build passed cleanly with `next build`.
- [x] **Responsive Layouts**: Desktop (1280px+), Tablet (768px - 1024px), and Mobile (&lt;640px) verified.
- [x] **Loading States**: Skeletons and spinners present during async data retrieval across all components.
- [x] **Error Boundaries & Retries**: `TrendChart` and `CongestionHeatmap` render structured error containers with immediate retry triggers.
- [x] **Dual Simulation / Live Backend**: Toggle in the navigation bar allows seamless switching between FastAPI live API (port 8000) and local telemetry simulation.
