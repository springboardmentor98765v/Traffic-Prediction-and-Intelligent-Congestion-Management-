# TrafficVision AI — Milestone 3 UI Wireframes & Layout Specifications

## Overview
This document specifies the user interface wireframes and component interaction designs for **Milestone 3**:
1. **Notification Bell & Floating Alerts Flyout Component (`NotificationBell.tsx`)**
2. **Analytics Dashboard with Longitudinal Trend Chart (`TrendChart.tsx`)**
3. **7×24 Diurnal Congestion Heatmap Matrix (`CongestionHeatmap.tsx`)**
4. **AI Recommendations Panel & Impact Simulation Modal (`AIRecommendationsPanel.tsx`)**
5. **Historical Report Export Dialog (`ReportExportModal.tsx`)**

---

## 1. Notification Bell & Floating Alerts Flyout Wireframe

### Location & Interaction
Omnipresent in the top navigation bar header (`Navbar.tsx`). Displays a real-time badge count of unread/active incidents with an animated pulsing ping on critical emergencies.

```text
+--------------------------------------------------------------------------------------------------+
| [🚦 TrafficVision AI]  [Dashboard] [Live Map] [Route Analysis] [Predictions] [Alerts]  | 🔔(3) [Admin]|
+------------------------------------------------------------------------------------------+-------+
                                                                                           |
                                               +-------------------------------------------+-----+
                                               | LIVE INCIDENT ALERTS               [Resolve All] |
                                               | 3 active incidents                               |
                                               +-------------------------------------------------+
                                               | [All (3)]  [🔴 Critical (1)]  [🟡 Warning (2)]    |
                                               +-------------------------------------------------+
                                               | 🔴 Station Road • 3m ago             [CRITICAL] |
                                               | Severe Congestion & Queue Spillback             |
                                               | Density: 82.1% approaching terminal junction    |
                                               | 🤖 Dispatch officer & +25s green phase          |
                                               | [Status: Active]           [Ack]  [Resolve]     |
                                               +-------------------------------------------------+
                                               | 🟡 MG Road • 11m ago                  [WARNING] |
                                               | Rush Hour Volume Surge                          |
                                               | Volume up 28% in 10 mins. Density: 78.4%        |
                                               | 🤖 Broadcast VMS advisory to divert to Ring Rd  |
                                               | [Status: Ack'd]                   [Resolve]     |
                                               +-------------------------------------------------+
                                               | 🔵 Airport Road • 25m ago            [ADVISORY] |
                                               | Optimal Free-Flow Velocity (62 km/h)            |
                                               | [Status: Resolved ✓]                            |
                                               +-------------------------------------------------+
                                               |       [ View Complete Incident Center → ]       |
                                               +-------------------------------------------------+
```

---

## 2. Analytics Dashboard & Multi-Metric Trend Chart Wireframe (`/analytics`)

### Purpose
Longitudinal time-series analysis comparing network average volume vs corridor-specific densities across 24-hour diurnal curves, 7-day windows, and 30-day capacity trends.

```text
+--------------------------------------------------------------------------------------------------+
|  TRAFFIC ANALYTICS & HISTORICAL TRENDS                          [ 📥 Download Historical Report ] |
|  Diurnal pattern evaluation, 7×24 congestion heatmap matrix, and predictive AI intelligence     |
|                                                                                                  |
|  +--------------------+ +--------------------+ +--------------------+ +------------------------+ |
|  | AI HEURISTIC       | | PEAK LEAD TIME     | | CARBON OFFSET      | | ACTIVE OPTIMIZATIONS   | |
|  | 88.4% Precision    | | 22 min early warn  | | -14.2% Idle saving | | 3 Active Interventions | |
|  +--------------------+ +--------------------+ +--------------------+ +------------------------+ |
|                                                                                                  |
|  +---------------------------------------------------------------------------------------------+ |
|  | 📈 TRAFFIC DENSITY & FLOW VELOCITY TRENDS         [Citywide Avg | Corridors]  [24h | 7d | 30d]  | |
|  | Dotted line represents 65% Critical Gridlock Threshold                                      | |
|  |                                                                                             | |
|  | 100%|                                                                                       | |
|  |     |                       (Morning Peak)                    (Evening Commute)             | |
|  |  75%|                          /---\                             /-----\                    | |
|  | - - | - - - - - - - - - - - - / - - \ - - - - - - - - - - - - - / - - - \ - - - - (65% Crit)| |
|  |  50%|                        /       \       (Midday)          /         \                  | |
|  |     |                       /         \-----/--------\        /           \                 | |
|  |  25%|           /----------/                          \------/             \------\         | |
|  |   0%|----------/                                                                   \--------| |
|  |     +---------------------------------------------------------------------------------------+ |
|  |       00h  02h  04h  06h  08h  10h  12h  14h  16h  18h  20h  22h  24h                       | |
|  |                                                                                             | |
|  |  [Avg Density: 52.4%]  [Mean Speed: 38.6 km/h]  [Peak Crest: 88.0%]  [Peak Hour: 18:00]     | |
|  +---------------------------------------------------------------------------------------------+ |
+--------------------------------------------------------------------------------------------------+
```

---

## 3. 7×24 Diurnal Congestion Heatmap Matrix Wireframe

### Purpose
Color-coded density intensity across 168 individual day/hour blocks to detect recurrent bottleneck windows.

```text
+--------------------------------------------------------------------------------------------------+
|  🔥 7×24 DIURNAL CONGESTION HEATMAP MATRIX                Corridor Scope: [ Citywide Average ▼ ] |
|                                                                                                  |
|       00h 02h 04h 06h 08h 10h 12h 14h 16h 18h 20h 22h                                            |
|  MON: [░] [░] [░] [▒] [█] [▓] [▒] [▒] [▓] [█] [▓] [▒]                                            |
|  TUE: [░] [░] [░] [▒] [█] [▓] [▒] [▒] [▓] [█] [▓] [▒]                                            |
|  WED: [░] [░] [░] [▒] [█] [▓] [▒] [▒] [▓] [█] [▓] [▒]                                            |
|  THU: [░] [░] [░] [▒] [█] [▓] [▒] [▒] [▓] [█] [▓] [▒]                                            |
|  FRI: [░] [░] [░] [▒] [█] [▓] [▒] [▓] [█] [█] [█] [▓]  <-- Worst congestion window               |
|  SAT: [░] [░] [░] [░] [▒] [▒] [▓] [▓] [▓] [▓] [▒] [░]                                            |
|  SUN: [░] [░] [░] [░] [░] [▒] [▒] [▒] [▓] [▒] [░] [░]                                            |
|                                                                                                  |
|  +---------------------------------------------------------------------------------------------+ |
|  | Hover Inspection: Friday • 18:00 | Density: 94% | Speed: 16 km/h | Risk: CRITICAL BOTTLENECK| |
|  +---------------------------------------------------------------------------------------------+ |
|  Legend: [░] Fluid (<25%)  [▒] Moderate (25-45%)  [▓] Heavy (45-65%)  [█] Critical (>65%)       |
+--------------------------------------------------------------------------------------------------+
```

---

## 4. AI Recommendations Panel & Simulation Modal Wireframe

### Purpose
Actionable AI decision support providing one-click signal retiming, bypass diversions, and quantified before/after simulation comparisons.

```text
+--------------------------------------------------------------------------------------------------+
|  🤖 AI DECISION SUPPORT & MITIGATION RECOMMENDATIONS                 [Pending (2)] [Applied (1)] |
|                                                                                                  |
|  +-------------------------------------------------+ +-----------------------------------------+ |
|  | 🚦 Station Road Ingress Retiming   [CRITICAL]   | | 🧭 MG Road to Outer Ring Bypass  [HIGH] | |
|  | Station Road (R003) • J-104 North Ingress       | | MG Road (R001) • Victoria Flyover J-082 | |
|  | Density: 82.1% • Queue growing 18 veh/min       | | Density: 78.4% • Ingress volume surge   | |
|  | Plan: Extend northbound green cycle +25s (70s)  | | Plan: Divert 20% traffic via VMS signs  | |
|  |                                                 | |                                         | |
|  | Delay Cut: -34% | Speed: +8.5 km/h | CO2: -16%  | | Delay Cut: -22% | Speed: +6.2 | CO2: -11%| |
|  | [🔬 Simulate Impact]     [⚡ Apply Optimization]| | [🔬 Simulate Impact]   [⚡ Apply Optim]  | |
|  +-------------------------------------------------+ +-----------------------------------------+ |
+--------------------------------------------------------------------------------------------------+
                                   |
              (When "Simulate Impact" is clicked)
                                   v
+----------------------------------------------------------------------------------+
| 🔬 TRAFFIC INTERVENTION SIMULATION OUTCOME                                   [✕] |
| Before vs After Algorithmic Optimization Comparison                              |
|                                                                                  |
| Transit Delay (minutes):                                        -34% Reduction   |
| Baseline:   [===========================================] 24.5 min               |
| Simulated:  [======================                     ] 16.2 min               |
|                                                                                  |
| Congestion Density (%):                                                          |
| Baseline:   [=====================================      ] 82.1%                  |
| Simulated:  [===========================                ] 58.4%                  |
|                                                                                  |
| Physical Queue Spillback Length:                                -62% Length Cut  |
| Baseline:   [===========================================] 850m                   |
| Simulated:  [=================                          ] 320m                   |
|                                                                                  |
| [ Close Simulation ]                                   [ ⚡ Apply Optimization ] |
+----------------------------------------------------------------------------------+
```

---

## 5. Historical Report Download Modal Wireframe

### Purpose
Exports historical telemetry, incidents, and optimization audits in CSV, JSON, or Executive Print-Ready HTML/PDF format.

```text
+----------------------------------------------------------------------------------+
| 📥 HISTORICAL TRAFFIC & CONGESTION REPORT EXPORT                             [✕] |
|                                                                                  |
| Temporal Window:                                                                 |
| [ (•) Last 24 Hours ]     [ ( ) Past 7 Days ]     [ ( ) Last 30 Days ]           |
|                                                                                  |
| Corridor Scope:                                                                  |
| [ Entire City Network (All Corridors)                                         ▼ ]|
|                                                                                  |
| Datasets to Include:                                                             |
| [✓] Sensor Telemetry (Volume/Speed)       [✓] Incidents & Alerts                 |
| [✓] AI Decision Logs & Audit Trails       [✓] CO2 & Eco Metrics                  |
|                                                                                  |
| Select Export Format:                                                            |
| +---------------------+   +---------------------+   +--------------------------+ |
| |   📄 Download CSV   |   |   ⚙️ Download JSON   |   |   📊 Executive Report    | |
| | (Spreadsheet Data)  |   | (Data Pipeline API) |   | (Print-Ready HTML / PDF) | |
| +---------------------+   +---------------------+   +--------------------------+ |
+----------------------------------------------------------------------------------+
```
