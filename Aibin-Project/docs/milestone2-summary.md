# TrafficVision AI — Milestone 2: Backend Architecture & Integration Summary

**Role:** Intern 1 (Team Lead / Backend & Integration)  
**Milestone:** Milestone 2 — Traffic Prediction & Route Optimization  
**Project:** TrafficVision AI  
**Date:** September 2026  

---

## 1. Executive Summary

Milestone 2 expands the **TrafficVision AI** backend from the foundational Authentication and RBAC core into an intelligent, microservice-backed routing and prediction platform. 

As Intern 1 (Team Lead & Backend Integration), the primary objectives achieved during Milestone 2 were:
1. Designing and building the **Route Analysis Microservice** (`route_analysis` running on port `8002`).
2. Developing an **OpenStreetMap (OSRM) integration wrapper** with intelligent fallback to mathematical Haversine routing and localized LRU in-memory caching.
3. Exposing and registering the four core route optimization endpoints (`/optimize`, `/alternate`, `/travel-time`, `/conditions`) under the API Gateway (`/api/v1/route/*`).
4. Connecting the Route Analysis Service and Gateway with **Intern 3's AI/ML Engine** (`ai_engine` running on port `8001`) for congestion-aware route re-ranking and live+predicted travel time estimation.
5. Bridging the Gateway to **Intern 2's Data Engineering Service** (`anmol-data`) for live road condition telemetry.
6. Enforcing role-based access control (RBAC), token validation, and rate-limiting across all route analysis and predictive query entrypoints.
7. Achieving 100% test pass rate across the automated test suite (`18/18` tests passing).

---

## 2. System Architecture & Topology

```
                                      +-----------------------------------+
                                      |         Frontend Client           |
                                      | (Hariom - Intern 4 / Port 3000)   |
                                      +-----------------+-----------------+
                                                        |
                                            Bearer JWT  | HTTP Requests
                                                        v
                                      +-----------------------------------+
                                      |            API Gateway            |
                                      |     (Aibin - Intern 1 / Port 8080)|
                                      |  - Auth & RBAC Verification       |
                                      |  - Rate Limiting                  |
                                      |  - Centralized OpenAPI Docs       |
                                      +--------+-----------------+--------+
                                               |                 |
                   Proxy /api/v1/route/*       |                 | Proxy /api/v1/predict/*
                                               v                 v
           +---------------------------------------+   +------------------------------------+
           |       Route Analysis Service          |   |            AI/ML Engine            |
           |    (Aibin - Intern 1 / Port 8002)     |   |   (Saksham - Intern 3 / Port 8001) |
           |  - /optimize                          |   |  - /predict/congestion             |
           |  - /alternate                         |   |  - /predict/delay                  |
           |  - /travel-time                       |   |  - /predict/peak-hours             |
           |  - /conditions                        |   |  - /predict/routes/rank            |
           +---------+-------------------+---------+   +------------------------------------+
                     |                   |                                 ^
      OSRM Queries   |                   | Direct Service-to-Service       |
                     v                   +---------------------------------+
           +--------------------+                      (Congestion & Ranking)
           | OpenStreetMap OSRM |
           | (Public / Local)   |
           +--------------------+
```

---

## 3. Microservice Specifications & Port Allocation

| Microservice | Port | Ownership | Responsibilities |
|---|---|---|---|
| **API Gateway** | `8080` | Intern 1 (`aibin-backend`) | Auth, RBAC, Rate-Limiting, Reverse-Proxy routing, Swagger docs (`/docs`). |
| **Route Analysis Service** | `8002` | Intern 1 (`aibin-backend`) | OSRM routing, waypoint geometry calculation, multi-candidate alternate routing, conditions lookup. |
| **AI/ML Engine** | `8001` | Intern 3 (`saksham-aiml`) | ML congestion forecasting, delay regression, peak-hour probability, multi-criteria route ranking. |
| **Data Engineering / Traffic API** | `8000` | Intern 2 (`anmol-data`) | Camera feeds, YOLO vehicle counts, real-time road conditions, speed metrics. |
| **PostgreSQL Database** | `5432` | Shared (`aibin-backend`) | User credentials, roles (`admin`, `traffic_operator`, `city_planner`, `commuter`), session tokens. |

---

## 4. Route Analysis Endpoints Catalog

All endpoints are registered under `/api/v1/route` on the API Gateway (`8080`) and proxy directly to the Route Analysis Service (`8002`).

### 1. Optimize Route — `POST /api/v1/route/optimize`
- **Purpose:** Calculates the single optimal route between origin and destination coordinates.
- **Access Role:** `commuter`, `traffic_operator`, `city_planner`, `admin`.
- **Request Body:**
  ```json
  {
    "origin": { "lat": 12.9716, "lng": 77.5946 },
    "destination": { "lat": 12.9352, "lng": 77.6245 },
    "preferences": {
      "avoid_tolls": false,
      "avoid_highways": false,
      "mode": "driving"
    }
  }
  ```
- **Response Shape (`200 OK`):**
  ```json
  {
    "route_id": "rt_opt_12.9716_77.5946_12.9352_77.6245",
    "distance_km": 5.42,
    "duration_min": 14.8,
    "confidence_score": 0.95,
    "waypoints": [
      { "lat": 12.9716, "lng": 77.5946, "instruction": "Start navigation" },
      { "lat": 12.9534, "lng": 77.6095, "instruction": "Continue along primary arterial" },
      { "lat": 12.9352, "lng": 77.6245, "instruction": "Arrive at destination" }
    ],
    "source": "osrm",
    "cached": false
  }
  ```

---

### 2. Alternate Routes — `POST /api/v1/route/alternate`
- **Purpose:** Computes 2–3 alternate route candidates, queries Intern 3's AI Engine to evaluate congestion probability along each path, and returns candidates ranked by lowest predicted delay.
- **Access Role:** `commuter`, `traffic_operator`, `city_planner`, `admin`.
- **Request Body:**
  ```json
  {
    "origin": { "lat": 12.9716, "lng": 77.5946 },
    "destination": { "lat": 12.9352, "lng": 77.6245 },
    "max_alternatives": 3
  }
  ```
- **Response Shape (`200 OK`):**
  ```json
  {
    "query": { "origin": { "lat": 12.9716, "lng": 77.5946 }, "destination": { "lat": 12.9352, "lng": 77.6245 } },
    "total_routes_found": 3,
    "routes": [
      {
        "rank": 1,
        "route_id": "rt_alt_0",
        "route_label": "Primary via Central Corridor",
        "distance_km": 5.42,
        "duration_min": 14.8,
        "predicted_delay_min": 2.1,
        "congestion_level": "LOW",
        "score": 0.92,
        "waypoints": [ { "lat": 12.9716, "lng": 77.5946 }, { "lat": 12.9352, "lng": 77.6245 } ]
      },
      {
        "rank": 2,
        "route_id": "rt_alt_1",
        "route_label": "Alternate via Ring Bypass",
        "distance_km": 6.81,
        "duration_min": 17.2,
        "predicted_delay_min": 4.5,
        "congestion_level": "MODERATE",
        "score": 0.81,
        "waypoints": [ { "lat": 12.9716, "lng": 77.5946 }, { "lat": 12.9352, "lng": 77.6245 } ]
      }
    ]
  }
  ```

---

### 3. Travel Time Estimation — `POST /api/v1/route/travel-time`
- **Purpose:** Produces high-fidelity ETA estimates combining geometric baseline distance, historical time-of-day multipliers, live traffic telemetry, and ML congestion predictions.
- **Access Role:** `commuter`, `traffic_operator`, `city_planner`, `admin`.
- **Request Body:**
  ```json
  {
    "origin": { "lat": 12.9716, "lng": 77.5946 },
    "destination": { "lat": 12.9352, "lng": 77.6245 },
    "departure_time": "2026-09-16T17:30:00"
  }
  ```
- **Response Shape (`200 OK`):**
  ```json
  {
    "distance_km": 5.42,
    "baseline_duration_min": 10.84,
    "estimated_duration_min": 16.34,
    "predicted_delay_min": 5.5,
    "traffic_condition": "MODERATE",
    "confidence": 0.91,
    "departure_time": "2026-09-16T17:30:00",
    "based_on": "live+predicted"
  }
  ```

---

### 4. Road Conditions — `GET /api/v1/route/conditions`
- **Purpose:** Inspects active road status, incidents, and surface conditions for a corridor, querying Intern 2's Data Engineering service with local fallback.
- **Access Role:** `commuter`, `traffic_operator`, `city_planner`, `admin`.
- **Parameters:** `road_id` (Query string, e.g. `ROAD_MG_ROAD` or `CBD_CORRIDOR_01`).
- **Response Shape (`200 OK`):**
  ```json
  {
    "road_id": "ROAD_MG_ROAD",
    "status": "CONGESTED",
    "condition_status": "Heavy Traffic",
    "surface_condition": "Dry",
    "active_incidents": 1,
    "incident_description": "Lane 2 bottleneck near Metro Station",
    "average_speed_kmh": 22.4,
    "source": "live_telemetry"
  }
  ```

---

## 5. Components: Real Implementations vs Fallback Stubs

To ensure continuous operation during development and isolated testing, every integration layer uses a **Real-First with Resilient Fallback** design pattern:

| Component | Primary Engine (Real) | Fallback Mechanism (Offline / Stub) | Resiliency Trigger |
|---|---|---|---|
| **Route Geometry & ETA** | OpenStreetMap Public / Local OSRM REST API (`http://router.project-osrm.org`) | Mathematical Haversine Great-Circle routing with multi-waypoint interpolation. | OSRM timeout (`> 3.0s`), HTTP 5xx error, or network isolation. |
| **Route Caching** | Local In-Memory LRU Cache (`ROUTE_CACHE` with TTL and coordinate hashing). | Dynamic re-computation. | Cache miss or expired TTL. |
| **Congestion Prediction** | HTTP calls to Intern 3's AI Engine (`POST /predict/congestion` & `POST /predict/routes/rank`). | Time-of-day heuristic model with peak-hour multipliers (Morning 8–10 AM, Evening 5–8 PM). | AI Engine microservice uncontactable or down. |
| **Road Conditions** | HTTP calls to Intern 2's Data API (`GET /traffic/conditions/{road_id}`). | Local condition catalog indexed by road identifier pattern. | Data microservice uncontactable or empty response. |
| **Service Proxying** | Asynchronous HTTP Gateway Proxy (`httpx.AsyncClient`). | In-process internal router routing (`route_analysis.router`). | Target service container unresponsive. |

---

## 6. Teammate Coordination & Contract Flags

### Flag 1: Intern 2 (Data Engineering — `anmol-data`)
- **Status:** Integrated.
- **Contract Note:** In the early SRS drafts, the condition endpoint was proposed as `/api/v1/traffic/road-condition/{road_id}`. In Intern 2's code (`anmol-data/Api/traffic_api.py`), the endpoint is exposed as `GET /traffic/conditions/{road_id}`.
- **Resolution:** Intern 1's backend seamlessly connects to `GET /traffic/conditions/{road_id}` and maps fields (`condition_status`, `description`, `speed`) into the standardized Gateway contract.

### Flag 2: Intern 3 (AI/ML Engine — `saksham-aiml`)
- **Status:** Integrated.
- **Contract Note:** Intern 3 provides predictive models via `/predict/congestion`, `/predict/delay`, and route scoring via `/predict/routes/rank`.
- **Resolution:** Intern 1's Route Analysis service passes geometric candidate routes to `/predict/routes/rank`, combining OSRM waypoint distances with ML delay predictions for final ordering.

### Flag 3: Intern 4 (Frontend — `hariom-frontend`)
- **Status:** Ready for frontend consumption.
- **Contract Alignment:** All endpoints match the specifications outlined in `docs/route-analysis-contract.md`. Responses provide coordinates in `[lat, lng]` structure ready for Leaflet / Mapbox rendering.

---

## 7. Milestone 1 Sanity Check

All Milestone 1 deliverables remain fully functional, regression-tested, and verified:
- **Authentication:** `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`.
- **RBAC Enforcement:** `GET /api/v1/auth/me`, role hierarchy checks (`admin`, `traffic_operator`, `city_planner`, `commuter`), denial of unauthorized routes with HTTP `403 Forbidden`.
- **Database Schema:** Fully compatible with PostgreSQL DDL (`database/schema.sql`).

---

## 8. Milestone 3 Handoff & Future Roadmap

When transitioning into Milestone 3 (Real-Time Edge Analytics, Incident Dispatch & Live WebSockets):
1. **WebSocket Streaming:** Expose `/ws/route/{route_id}/live` for real-time turn-by-turn re-routing when sudden incidents occur.
2. **Incident Dispatch Webhooks:** Connect Intern 2's YOLO automated incident detection to trigger auto-recalculation alerts in Route Analysis.
3. **Redis Centralized Cache:** Transition from in-memory Python dictionaries to a distributed Redis cache for multi-instance horizontal scaling.

---
*Authored by Intern 1 (Team Lead / Backend & Integration) — TrafficVision AI Team*
