# TrafficVision AI — Milestone 3 Frontend Technical Plan

## Overview
Milestone 3 elevates the TrafficVision AI platform into a complete intelligent command and analytical system. It introduces an omnipresent **Notification Bell & Alerts Flyout**, an advanced **Analytics Dashboard** featuring multi-metric trend charts and a 7×24 diurnal congestion heatmap, an **AI Recommendations Panel** with real-time algorithmic impact simulation, and a **Historical Report Download Center**.

---

## Sprint Roadmap (Days 1 – 7)

| Day | Task Description | Expected Output / Deliverable | Depends On | Provides To |
|---|---|---|---|---|
| **Day 1** | Review Milestone 1 & 2 frontend; plan Milestone 3 additions (Notification Bell, Analytics Dashboard trend charts + heatmap, AI Recommendations panel). Sketch wireframes. | M3 frontend plan (`milestone3-plan.md`); wireframes for Alerts, Analytics, Recommendations (`milestone3-wireframes.md`) | Milestone 2 frontend (complete) | Self (Day 2 build) |
| **Day 2** | Build Notification Bell component (icon + dropdown list of messages) using mock alert data initially, matching the visual pattern of existing dashboard. | Notification Bell UI built with mock data (`NotificationBell.tsx`) | Own wireframes | Self (Day 3 real-data wiring) |
| **Day 3** | Connect Notification Bell to Intern 1's real Alert API (`GET /alerts/my`, mark as read); show unread-count badge. | Notification Bell working with real alerts (`api.getAlerts()`); unread badge functional | Intern 1's Alert delivery endpoints | Intern 5 (UI test target) |
| **Day 4** | Build Analytics Dashboard page with trend charts using Intern 2's `/analytics/trends` endpoint. | Trend charts rendering real data on Analytics Dashboard (`TrendChart.tsx`) | Intern 2's trend analysis endpoint | Intern 5 (dashboard test target) |
| **Day 5** | Add congestion heatmap visualization using Intern 2's `/analytics/heatmap` endpoint, AI Recommendations panel using Intern 3's `/ai/recommendations` endpoint, and historical-report download button. | Heatmap (`CongestionHeatmap.tsx`) + AI recommendations (`AIRecommendationsPanel.tsx`) + report-download (`ReportExportModal.tsx`) live | Intern 2's heatmap/reports; Intern 3's recommendations | Intern 5 (full UI test target) |
| **Day 6** | UI polish, responsiveness fixes, error/loading states for alert, analytics and AI calls; fix defects reported during QA integration cycle. | Stable, polished Alerts + Analytics + AI Insights UI with error boundaries and loading skeletons | Intern 5's defect log | Intern 5 (regression build) |
| **Day 7** | Final UI fixes from QA feedback; rehearse full demo flow (Login → Live Dashboard → Route Analysis → Analytics/Heatmaps → Alerts → AI Recommendations); write frontend module notes. | Demo-ready frontend; module documentation (`milestone3-module-notes.md`) | Passed regression | Milestone 3 final demo |

---

## API Contract Specifications for Milestone 3

### 1. Alert API (Intern 1)
- **`GET /api/v1/alerts/my`**
  - Query: `?status=active|acknowledged|resolved&severity=critical|warning|advisory`
  - Response `200 OK`:
  ```json
  [
    {
      "id": "ALT-101",
      "road_id": "R003",
      "road_name": "Station Road",
      "severity": "critical",
      "title": "Severe Congestion & Queue Spillback",
      "message": "Density sustained above 82% for over 15 minutes.",
      "timestamp": "2026-09-22T17:30:00Z",
      "status": "active",
      "action_recommended": "Extend northbound green signal by 25s"
    }
  ]
  ```
- **`POST /api/v1/alerts/{alert_id}/read`** (or `acknowledge`)
  - Response `200 OK`: `{ "success": true, "alert_id": "ALT-101", "status": "acknowledged" }`

### 2. Analytics Trends & Heatmap API (Intern 2)
- **`GET /api/v1/analytics/trends?timeframe=24h|7d|30d&corridor_id={optional}`**
  - Response `200 OK`:
  ```json
  {
    "timeframe": "24h",
    "summary": {
      "avgDensity": 52.4,
      "avgSpeed": 38.6,
      "peakDensity": 88.0,
      "peakHour": "18:00",
      "totalVolume": 42850
    },
    "points": [
      {
        "timestamp": "2026-09-22T08:00:00Z",
        "label": "08:00",
        "network_avg_density": 82.5,
        "network_avg_speed": 22.0,
        "corridor_densities": {
          "R001": 78.4,
          "R002": 45.2,
          "R003": 89.1,
          "R004": 18.0,
          "R005": 35.0
        }
      }
    ]
  }
  ```
- **`GET /api/v1/analytics/heatmap?corridor_id={optional}`**
  - Response `200 OK`: Array of 168 objects (7 days × 24 hours).
  ```json
  [
    {
      "day_index": 0,
      "day_name": "Mon",
      "hour": 8,
      "density": 84.0,
      "speed": 21.0,
      "congestion_level": "High",
      "incident_risk": "critical",
      "volume_count": 240
    }
  ]
  ```

### 3. AI Recommendations API (Intern 3)
- **`GET /api/v1/ai/recommendations`**
  - Response `200 OK`:
  ```json
  [
    {
      "id": "REC-101",
      "title": "Station Road Ingress Green Phase Extension",
      "category": "signal_retiming",
      "priority": "critical",
      "target_corridor_id": "R003",
      "target_corridor_name": "Station Road",
      "impact_delay_reduction_pct": 34,
      "impact_speed_gain_kmh": 8.5,
      "impact_co2_offset_pct": 16.2,
      "confidence": 0.94,
      "status": "pending",
      "simulation": {
        "baseline_delay_min": 24.5,
        "optimized_delay_min": 16.2,
        "baseline_density_pct": 82.1,
        "optimized_density_pct": 58.4,
        "queue_length_meters_before": 850,
        "queue_length_meters_after": 320
      }
    }
  ]
  ```
- **`POST /api/v1/ai/recommendations/{rec_id}/apply`**
  - Response `200 OK`: `{ "success": true, "rec_id": "REC-101", "status": "applied", "applied_at": "..." }`
