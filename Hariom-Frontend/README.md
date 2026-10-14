# 🚦 TrafficVision AI — Intelligent Traffic Prediction & Congestion Management

> **Next-Generation Urban Traffic Intelligence Command Center**  
> Developed for Springboard AI Internship • **Frontend & Application Services (Milestones 1, 2 & 3)**  
> **Owner**: Hariom (Intern 4 — Frontend Lead)

[![Next.js](https://img.shields.io/badge/Next.js-15.1-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0-61dafb?style=for-the-badge&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38bdf8?style=for-the-badge&logo=tailwindcss)](https://tailwindcss.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-OpenStreetMap-10b981?style=for-the-badge&logo=leaflet)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

---

## 📌 Executive Summary

**TrafficVision AI** is an enterprise-grade cyber-aesthetic traffic monitoring, congestion mitigation, and route optimization platform. It bridges continuous machine learning predictions, algorithmic signal intervention, and geospatial OpenStreetMap vectoring into a reactive, real-time command dashboard.

The application features **Zero-Config Dual Telemetry**: it automatically communicates with live backend microservices (FastAPI / OSRM / ML models), while seamlessly falling back to high-fidelity localized simulation when offline.

---

## 🌟 Milestone Feature Breakdown

### 🎯 Milestone 1: Command Dashboard & Live Telemetry
- **Situational KPI Command Center**: Real-time City Congestion Index, Monitored Corridor Count, Network Flow Velocity, and Active Alert Metrics.
- **Geographic Network Map**: Interactive dark-mode Leaflet map rendering arterial corridors, density hotspots, and incident markers.
- **Corridor Inspection Drawer**: Detailed view for individual road segments with live density gauges, speed profiles, and capacity trends.
- **Role-Based Access Control (RBAC)**: Secure multi-tier sessions (`Admin`, `Operator`, `Public`) with quick-fill demo authentication.

### 🗺️ Milestone 2: Intelligent Route Optimization
- **AI-Powered Route Selection**: Evaluates live arterial congestion scores and OSRM geometry to compute the optimal path vs. gridlocked direct routes.
- **Multi-Route Side-by-Side Comparison**:
  - ⚡ **Recommended Bypass (Neon Cyan)**: Maximizes throughput and saves up to 34% travel time.
  - 🚗 **Alternate 1 (Direct Core Grid - Amber)**: Baseline path showing real-time queuing penalties.
  - 🌿 **Alternate 2 (Perimeter Parkway - Purple)**: Eco-friendly low-emission smooth flow path.
- **Corridor Telemetry Breakdown**: Per-segment table showing road IDs, surface friction, speed limits, and incident risk.

### 🚀 Milestone 3 (Latest Deliverables): Intelligence & Triage Suite
- 🔔 **Omnipresent Notification Bell & Alerts Flyout (`NotificationBell.tsx`)**:
  - Fixed top-bar drawer displaying real-time incident notifications.
  - Severity-filtered triage (`Critical`, `Warning`, `Advisory`, `All`).
  - Unread badge counter with animated pulsing warning beacons for critical incidents.
  - One-click incident acknowledgment and dispatch resolution.
- 📈 **Longitudinal Trend Chart (`TrendChart.tsx`)**:
  - Interactive multi-metric SVG time-series visualizer.
  - Temporal windows: **24-Hour Diurnal Curve**, **7-Day Longitudinal**, and **30-Day Capacity Trend**.
  - Citywide network average vs. individual corridor comparison with togglable corridor pills.
  - Interactive vertical crosshairs and floating data inspection tooltips.
- 🗓️ **7×24 Diurnal Congestion Heatmap Matrix (`CongestionHeatmap.tsx`)**:
  - 168-cell matrix mapping density across all 7 days and 24 hours.
  - Accurately highlights weekday rush-hour peaks vs. weekend diurnal patterns.
  - Interactive hover inspector revealing exact congestion %, flow speed, and bottleneck risk index.
  - Corridor-specific scope filtering.
- 🤖 **AI Decision Recommendations & Simulation (`AIRecommendationsPanel.tsx`)**:
  - Algorithmic decision engine recommending signal phase adjustments, dynamic detour broadcasts, and ramp metering.
  - **Live Impact Simulation Modal**: Compares quantified *Before vs After* metrics (Transit Delay, Capacity Density %, and Queue Spillback Length).
  - **"⚡ Apply Optimization Now"**: Instantly executes interventions and updates live network density.
- 🗺️ **Dynamic Map-Based Origin & Destination Selection (`route-analysis/page.tsx`)**:
  - **Direct Map Clicking**: Click anywhere on the map to place pins with interactive `🟢 Set Origin` & `🏁 Set Dest` popup dialogs.
  - **Interactive Selection Modes**: Dedicated `Pick Origin` and `Pick Destination` buttons that activate crosshair cursor mode.
  - **City Landmark Corridor Nodes**: All major transit hubs, business districts, airports, and tech parks visible on the map with custom category icons.
  - **Live GPS Integration**: Single-click "📱 My Location" using device geolocation.
  - **Exact Coordinates Editor**: Manual latitude/longitude numeric input.
- 📄 **Historical Report Export Center (`ReportExportModal.tsx`)**:
  - Generates downloadable compliance reports filtered by date range and corridors.
  - Export formats: **Spreadsheet CSV**, **Structured JSON**, and **Print-Ready Executive HTML/PDF Report**.

---

## 🏛️ Architecture & Component Hierarchy

```text
frontend/
├── app/
│   ├── layout.tsx                   # Root HTML shell & Theme styling
│   ├── page.tsx                     # Landing page & ecosystem overview
│   ├── globals.css                  # Tailwind CSS, Leaflet dark-tiles, Glassmorphism
│   ├── alerts/                      # Dedicated Incident Alert & Triage Center
│   │   └── page.tsx
│   ├── analytics/                   # Intelligence Center (Trend Charts + 7x24 Heatmap)
│   │   └── page.tsx
│   ├── dashboard/                   # Main Command Dashboard with KPIs & Live Map
│   │   └── page.tsx
│   ├── live-map/                    # Fullscreen Geographic Network Visualizer
│   │   └── page.tsx
│   ├── login/ & register/           # Multi-role Auth with Operator/Admin Demo Quick-Fill
│   │   └── page.tsx
│   ├── predictions/                 # Heuristic & ML Congestion Predictor Tool
│   │   └── page.tsx
│   ├── route-analysis/              # Dynamic Map Pinning & Route Optimization
│   │   └── page.tsx
│   ├── components/
│   │   ├── AIRecommendationsPanel.tsx # Decision support deck & simulation comparison modal
│   │   ├── Badge.tsx                # Status and severity badges
│   │   ├── Card.tsx                 # Glassmorphic cyber container with header actions
│   │   ├── CongestionHeatmap.tsx    # 7x24 Diurnal density matrix (168 cells)
│   │   ├── ErrorMessage.tsx         # Error boundaries with retry triggers
│   │   ├── Layout.tsx               # Sidebar + Navbar responsive scaffold
│   │   ├── LeafletMap.tsx           # Leaflet map with route vectors & dynamic markers
│   │   ├── LeafletMapWrapper.tsx    # SSR-safe dynamic map loader
│   │   ├── Navbar.tsx               # Top header with NotificationBell & Mode switcher
│   │   ├── NotificationBell.tsx     # Floating notification bell & alert drawer
│   │   ├── ReportExportModal.tsx    # Multi-format report export modal (CSV/JSON/HTML)
│   │   ├── RoadDetailModal.tsx      # Corridor historical modal
│   │   ├── Sidebar.tsx              # Navigation panel with role indicators
│   │   └── TrendChart.tsx           # Multi-metric SVG time-series visualizer
│   └── lib/
│       ├── api.ts                   # Unified API client with dual live/simulation fallback
│       ├── auth-context.tsx         # JWT session management & role-based switching
│       └── traffic-context.tsx      # Real-time polling & recommendation event dispatch
└── docs/
    ├── api-contracts.md             # Inter-microservice API specs
    ├── milestone1-walkthrough.md    # Milestone 1 verification walkthrough
    ├── milestone2-plan.md           # Milestone 2 architecture design
    ├── milestone2-wireframes.md     # Route analysis wireframes
    ├── milestone3-plan.md           # Milestone 3 technical roadmap (Days 1–7)
    ├── milestone3-wireframes.md     # Notification, Analytics, & Heatmap wireframes
    └── milestone3-module-notes.md   # Presentation rehearsal script & demo guide
```

---

## 💻 Tech Stack & Design System

| Layer | Technologies Used |
|---|---|
| **Framework** | Next.js 15 (App Router), React 19, TypeScript 5.7 |
| **Styling** | Tailwind CSS 4, Custom Glassmorphism, Neon Cyan & Indigo Accents |
| **Mapping Engine** | Leaflet 1.9, OpenStreetMap Vector Cartography |
| **Visualizations** | Custom Responsive SVG Data Charts, 7×24 Matrix Heatmap Grid |
| **Icons** | Lucide React, Custom Cyber Emojis |
| **Architecture** | Client-Side State (Context API), Dual Telemetry (FastAPI + Simulation) |

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- **Node.js**: v18.17.0 or higher
- **npm**: v9.0.0 or higher

### 2. Setup & Installation
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

### 3. Running Locally
```bash
# Start the development server
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser to launch TrafficVision AI.

### 4. Production Build Verification
```bash
# Compile and build the production bundle
npm run build

# Start the optimized production server
npm run start
```
*Builds cleanly with **zero TypeScript errors** and **12/12 prerendered static routes**.*

---

## 🎬 6-Step Demo Presentation Walkthrough

Follow this sequence for client or faculty demonstrations:

1. **Authentication & RBAC**:
   - Navigate to `/login`. Click **"Operator Demo"** to log in as an operator with decision support permissions.
2. **Situational Command Center**:
   - Navigate to `/dashboard`. Point out top KPIs and click the **Notification Bell** in the top navigation bar. Filter alerts and click **"Acknowledge"** to show real-time counter decrement.
3. **Interactive Route Analysis**:
   - Navigate to `/route-analysis`.
   - Click **"Pick Origin"** and click any location on the map to set a start point.
   - Click **"Pick Destination"** and select an end point.
   - Observe how the **Neon Cyan AI Bypass** and **Alternate Routes** recalculate dynamically with real travel times and distance savings.
4. **Analytics Trends & 7×24 Diurnal Heatmap**:
   - Navigate to `/analytics`.
   - Toggle **24h / 7d / 30d** timeframes and inspect the interactive crosshairs.
   - Scroll down to the **7×24 Diurnal Heatmap** to visualize Friday evening gridlock spikes.
5. **AI Recommendations & Simulation**:
   - In `/analytics` or `/dashboard`, locate the **AI Recommendations Panel**.
   - Click **"Simulate Impact"** on *Station Road Ingress Green Phase Extension* to view Before vs After queue reduction.
   - Click **"⚡ Apply Optimization Now"** to observe live corridor density reduction.
6. **Historical Report Export**:
   - Click **"Download Historical Report"**.
   - Select temporal parameters and click **"Executive Report"** or **"Download CSV"** to demonstrate immediate compliance reporting.

---

## 📄 License & Attribution

This project is licensed under the [MIT License](LICENSE).  
Developed as part of the **Springboard AI / ML & Full-Stack Intelligent Congestion Management** initiative.
