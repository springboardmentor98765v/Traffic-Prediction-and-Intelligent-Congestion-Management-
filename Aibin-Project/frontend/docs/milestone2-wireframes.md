# TrafficVision AI — Milestone 2 UI Wireframes & Layout Specifications

## Overview
This document specifies the user interface wireframes and component interaction designs for **Milestone 2**:
1. **Interactive Leaflet.js Map Component**
2. **Route Analysis & Congestion Avoidance Page (`/route-analysis`)**
3. **Route Comparison & Travel Time Telemetry (`/route/travel`)**
4. **Traffic Prediction Visualizations & Scenario Sandbox (`/predictions`)**

---

## 1. Route Analysis Page Wireframe (`/route-analysis`)

### Purpose
Allows city traffic operators and commuters to calculate optimal, congestion-avoiding routes between any two metropolitan nodes, compare primary vs alternate routes, and inspect segment-level telemetry.

```text
+--------------------------------------------------------------------------------------------------+
| [🚦 TrafficVision AI]  [Dashboard] [Live Map] [Route Analysis] [Predictions] [Alerts]  | [Admin]  |
+--------------------------------------------------------------------------------------------------+
|  ROUTE ANALYSIS & CONGESTION-AWARE ROUTING                                                       |
|                                                                                                  |
|  +-------------------------------------+ +-----------------------------------------------------+ |
|  | ROUTE PARAMETERS                    | | INTERACTIVE LEAFLET ROUTE MAP                       | |
|  |                                     | | (OpenStreetMap Tiles - Free / No Key Required)      | |
|  | Origin Node:                        | |                                                     | |
|  | [ 🟢 Station Road Hub (R003)    ▼ ] | |          [🏁 Airport Terminal (Dest)]               | |
|  |                                     | |                 /                                    | |
|  | Destination Node:                   | |     (Alt 1)   /      (Primary - Optimized)          | |
|  | [ 🏁 Airport Terminal (R004)    ▼ ] | |     =========/=========== [🟢 24 min - Fastest]     | |
|  |                                     | |     [🟡 32m] \                                      | |
|  | Optimization Preference:            | |               \                                     | |
|  | (•) ⚡ Fastest (AI-Assisted)        | |            (Junction)                               | |
|  | ( ) 🚗 Lowest Congestion Delay      | |               /                                     | |
|  | ( ) 🌿 Eco-Route (Lowest Emissions) | |     [🟢 Station Hub (Orig)]                         | |
|  |                                     | |                                                     | |
|  | [   Calculate Intelligent Route   ] | | [Legend: ── Primary (Cyan)  ┄┄ Alternate (Amber)]   | |
|  +-------------------------------------+ +-----------------------------------------------------+ |
|                                                                                                  |
|  ROUTE COMPARISON & TRAVEL-TIME BREAKDOWN (Consuming /route/travel)                              |
|  +-----------------------------------+ +--------------------------------+ +--------------------+ |
|  | ⚡ RECOMMENDED ROUTE (Fastest)    | | 🚗 ALTERNATE 1 (Ring Bypass)   | | 🌿 ALTERNATE 2     | |
|  | 24 min • 14.2 km • 38 km/h avg    | | 32 min • 17.8 km • 42 km/h avg | | 36 min • 15.0 km   | |
|  | Congestion Delay: +4 min (Low)    | | Congestion Delay: +8 min       | | Eco Score: 92/100  | |
|  | Saves 12 min vs. MG Road Gridlock | | +8 min vs recommended route    | | +12 min vs optimal | |
|  +-----------------------------------+ +--------------------------------+ +--------------------+ |
|                                                                                                  |
|  CORRIDOR CONDITIONS ALONG ROUTE:                                                                |
|  • Segment 1: Station Link (0.8 km) - Speed 35 km/h | Density 38% [Medium] | Road Condition: Normal|
|  • Segment 2: Outer Ring Arterial (9.4 km) - Speed 62 km/h | Density 18% [Low] | Optimal Flow    |
|  • Segment 3: Airport Access Ramp (4.0 km) - Speed 55 km/h | Density 22% [Low] | Free Flow       |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Interactive Leaflet Map Component Wireframe

### Purpose
Renders real geographic coordinates on OpenStreetMap raster tiles, with custom HTML DivIcons and color-coded polylines representing traffic density and path options.

```text
+-------------------------------------------------------------------------+
| [Leaflet Map Viewport: Lat: 12.9716, Lng: 77.5946, Zoom: 12]            |
|                                                                         |
|                                [🟢 Airport Pin]                         |
|                                      ▲                                  |
|                                     / \                                 |
|                                    /   \  <-- Neon Amber Polyline       |
|            Neon Cyan Polyline --> /     \     (Alternate Route 1)       |
|            (Fastest Route)       /       \                              |
|                                 /         \                             |
|                    [📍 MG Road Pin]        \                            |
|                            \                \                           |
|                             \                \                          |
|                     [🟢 Station Pin] ---- [🟡 Ring Road Pin]            |
|                            (Origin)                                     |
|                                                                         |
|  [Map Controls: Zoom In (+) | Zoom Out (-) | Recenter (🎯)]             |
|  [Layer Toggle: Dark Cyber Mode | Standard OpenStreetMap]               |
+-------------------------------------------------------------------------+
```

---

## 3. Traffic Prediction Visualizations Wireframe (`/predictions`)

### Purpose
Provides dynamic forecasting across time horizons (+15m, +30m, +1h, +2h), ML confidence indicators, and a scenario simulation sandbox.

```text
+--------------------------------------------------------------------------------------------------+
| [🚦 TrafficVision AI]  [Dashboard] [Live Map] [Route Analysis] [Predictions] [Alerts]  | [Admin]  |
+--------------------------------------------------------------------------------------------------+
|  AI CONGESTION PREDICTION & FORECASTING CENTER                                                   |
|                                                                                                  |
|  Forecast Time Horizon:                                                                          |
|  [ Now ]   [ +15 mins ]   [ +30 mins ]   [ +1 Hour ]   [ +2 Hours ]   [ +4 Hours (Peak Surge) ]  |
|                                                                                                  |
|  +--------------------+ +---------------------+ +---------------------+ +----------------------+ |
|  | AI Confidence Rate | | Predicted Bottleneck| | Morning Peak Window | | Evening Peak Window  | |
|  | 89.2% (High Conf)  | | Station Rd & MG Rd  | | 08:30 - 09:45 AM    | | 17:30 - 19:15 PM     | |
|  +--------------------+ +---------------------+ +---------------------+ +----------------------+ |
|                                                                                                  |
|  PREDICTED CORRIDOR CONGESTION PROBABILITIES (+30m Horizon):                                     |
|  • MG Road (R001):      [██████████████░░░░░░] 74% Probability of High Congestion (Peak Surge)   |
|  • Ring Road (R002):    [████████░░░░░░░░░░░░] 42% Probability (Moderate Throughput)             |
|  • Station Road (R003): [████████████████░░░░] 85% Probability of Severe Bottleneck (Action Req) |
|  • Airport Road (R004): [████░░░░░░░░░░░░░░░░] 20% Probability (Free Flow Velocity)              |
|  • Civil Lines (R005):  [██████░░░░░░░░░░░░░░] 30% Probability (Fluid Flow)                     |
|                                                                                                  |
|  SCENARIO SIMULATION SANDBOX (Test Dynamic Reroute Adaptation):                                  |
|  [⚡ Simulate Lane Closure on R001]  [🌧️ Simulate Torrential Rain]  [🚨 Event Traffic Surge]     |
+--------------------------------------------------------------------------------------------------+
```
