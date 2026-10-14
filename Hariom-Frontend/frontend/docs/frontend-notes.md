# TrafficVision AI — Frontend Module Notes (Milestone 1)

## System Architecture & Tech Stack
- **Framework**: Next.js 15 (App Router, TypeScript)
- **Styling**: Tailwind CSS 4 + custom CSS custom properties (obsidian cyber theme, glassmorphic filters, neon congestion palettes)
- **State Management**: React Context (`AuthContext`, `TrafficContext`) with local storage hydration
- **API Client**: `app/lib/api.ts` with transparent dual-mode fallback (FastAPI live backend at `http://localhost:8000/api/v1` + rich simulated drifting traffic telemetry when backend is offline)

---

## RBAC Claims Mapping

| Role | Permissions & Capabilities | UI Rendering Scope |
|---|---|---|
| **Admin** | Full system control, signal override, incident creation, user management, system health metrics | Access to all routes, Admin Command Panel, Emergency Override Modal, System Health Diagnostics |
| **Operator** | Traffic monitoring, incident acknowledgement, dispatch trigger, advisory broadcasting | Access to Dashboard, Live Map, Alerts, Dispatch Actions, Congestion Alert Resolution |
| **Public / Commuter** | Read-only live road congestion, delay estimates, detour advice | Read-only Dashboard, Live Map with route recommendations, Alerts feed |

---

## Route Breakdown

1. `/login`: Secure login portal with role-based JWT authentication, validation error alerts, and 1-click Quick Demo buttons for Admin, Operator, and Commuter.
2. `/register`: New user signup with role selection and input validation.
3. `/dashboard`: Command Center overview with city-wide congestion KPI cards, monitored corridors status table, road detail telemetry drawer with 24-hour historical chart, and mini live radar.
4. `/live-map`: High-fidelity interactive SVG road network topology with live particle velocity flows, status filters, and clickable node inspection popovers.
5. `/alerts`: Real-time incident management queue with priority filtering (Critical, Warning, Advisory) and role-gated acknowledge/resolve triggers.
6. `/analytics`: Hourly traffic distribution curve (morning & evening rush hour peaks), corridor comparison metrics, and CO2 emission reduction estimates.

---

## QA Defect Resolution & Edge Case Coverage

- **AUTH-001 to AUTH-004**: Validated empty field handling, malformed email warning, incorrect password banner, and successful session generation.
- **AUTH-005 to AUTH-008**: Validated role claim propagation, protected route redirection, and automatic bearer token persistence.
- **TRAFFIC-001 to TRAFFIC-008**: Tested network error resilience, graceful degradation to offline mock simulation, density summary aggregation, and 5-second polling lifecycles.
