# TrafficVision AI — Milestone 2 Frontend Technical Plan

## Overview
Milestone 2 expands the TrafficVision AI platform from monitoring individual arterial segments to comprehensive **Corridor Route Optimization**, **Interactive Geographic Mapping (Leaflet.js + OpenStreetMap)**, **Multi-Route Travel-Time & Road-Condition Analysis**, and **Forward-Looking Prediction Visualizations**.

---

## Sprint Roadmap (Days 1 - 4)

### Day 1: M1 Review & M2 Architecture Planning
- Review of Milestone 1 frontend foundation (Next.js 15, Tailwind CSS 4, dual-backend simulation fallback, RBAC state).
- Formalize Route Analysis and Prediction specs.
- Draft UI wireframes in `docs/milestone2-wireframes.md`.

### Day 2: Leaflet.js + OpenStreetMap Map Integration
- Install Leaflet and TypeScript definitions (`leaflet`, `@types/leaflet`).
- Build `LeafletMap.tsx` and dynamic SSR-safe wrapper `LeafletMapWrapper.tsx`.
- Connect free OpenStreetMap tile server (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`).
- Add cyber dark mode filter styling to tiles.
- Custom HTML DivIcon markers for Origin (Emerald Pin), Destination (Red Checkered Flag), and Corridor Beacons.
- Polyline rendering with glow effects for primary and alternate route paths.

### Day 3: Route Analysis Page (`/route-analysis`)
- Build the Route Analysis screen with:
  - Origin / Destination location selector.
  - Optimization preferences: Fastest (AI-assisted), Least Congested, Eco-Route.
  - Service integration with `/route/optimize` and `/route/alternate`.
  - Side-by-side route comparison cards.

### Day 4: Travel-Time, Road Conditions & Prediction Visualizations
- Consume `/route/travel` to render:
  - Estimated travel duration, baseline free-flow time, congestion penalty.
  - Sub-segment status table (segment length, speed, density, road surface condition, active incidents).
- Build the **Traffic Prediction Visualizations** page (`/predictions`):
  - Horizon time slider (Now, +15m, +30m, +1h, +2h, +4h).
  - Congestion probability heat bars per corridor.
  - Machine learning model confidence metrics.
  - Incident & weather simulation sandbox (test dynamic reroute response).

---

## API Contract Specifications

### 1. `POST /api/v1/route/optimize`
- **Request Body**:
```json
{
  "origin": "R003",
  "destination": "R004",
  "preference": "fastest"
}
```
- **Response `200 OK`**:
```json
{
  "route_id": "RT-OPT-001",
  "name": "Outer Ring Express Bypass",
  "preference": "fastest",
  "distance_km": 14.2,
  "travel_time_minutes": 24,
  "baseline_time_minutes": 16,
  "congestion_delay_minutes": 4,
  "average_speed_kmh": 38.5,
  "congestion_level": "Low",
  "corridors": ["R003", "R002", "R004"],
  "coordinates": [
    [12.9784, 77.5684],
    [12.9352, 77.6245],
    [13.0125, 77.6582]
  ],
  "savings_minutes_vs_baseline": 12,
  "eco_score": 88
}
```

### 2. `POST /api/v1/route/alternate`
- **Response `200 OK`**: List of alternative routes with distance, travel time, and congestion levels.

### 3. `GET /api/v1/route/travel?route_id={route_id}`
- **Response `200 OK`**: Segment-by-segment road condition breakdown.
