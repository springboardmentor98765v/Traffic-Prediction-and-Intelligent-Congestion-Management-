# TrafficVision AI - Dependency Tracking

## Active Dependencies

| ID | Service | Dependency | Status | Notes |
|---|---|---|---|---|
| DEP-01 | anmol-data | Traffic Threshold Feed | 🚫 **Blocked** | Missing logic to push threshold breach alerts to `POST /api/v1/alerts`. Gateway proxy timeout increased to 40.0s for analytics workaround. Internal poller is acting as a TEMP STOPGAP for alerts. |
| DEP-02 | saksham-aiml | Prediction Models | ✅ Resolved | Congestion, delay, peak-hours, and route ranking are operational. |
| DEP-03 | saksham-aiml | Anomaly Feed | 🚫 **Blocked** | Missing logic to push predicted anomaly alerts to `POST /api/v1/alerts`. Internal poller is acting as a TEMP STOPGAP. |
| DEP-04 | route_analysis | Pathfinding | ✅ Resolved | Optimization, alternate routes, travel-time, and conditions are working. |
| DEP-05 | alert_service | Notifications | ✅ Resolved | Alerts, read status, and trigger scripts are working. |
