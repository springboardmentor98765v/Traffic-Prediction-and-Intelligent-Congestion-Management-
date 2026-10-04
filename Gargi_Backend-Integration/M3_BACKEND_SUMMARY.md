# TrafficVision M3 Backend Summary

## Milestone
Milestone 3 - Alerts, Analytics & AI Insights

## Owner
Gargi - Backend & Integration

## Backend Service
- FastAPI backend
- Host port: 8002
- PostgreSQL database: trafficvision

## Alert Service

Implemented and integrated:
- Congestion alerts
- Accident / possible-incident alerts from AI anomaly integration
- Road closure alerts
- Traffic delay alerts
- Role-scoped in-app alert recipients
- Alert read/unread state
- Active alert retrieval
- Congestion alert synchronization with Sharmila's monitoring service

### Alert Endpoints
- POST /api/v1/alerts
- GET /api/v1/alerts/my
- POST /api/v1/alerts/{alert_id}/read
- GET /api/v1/alerts/active
- POST /api/v1/alerts/sync/congestion

## Analytics Service

Implemented and verified:
- Traffic trends
- Traffic heatmap data
- Historical JSON reports
- Historical CSV reports

### Analytics Endpoints
- GET /api/v1/analytics/trends
- GET /api/v1/analytics/heatmap
- GET /api/v1/analytics/reports?format=json
- GET /api/v1/analytics/reports?format=csv

## Role-Based Alert Delivery

Alerts are scoped through AlertRecipient records.

- Admin: receives alerts
- Operator: receives alerts
- Public: receives public/high-severity alerts

The frontend notification bell polls the backend periodically and displays unread alert counts.

## Integration

Integrated:
- Central backend
- PostgreSQL
- Sharmila traffic-monitoring alert feed
- Manasa AI anomaly alert flow
- Samruddhi frontend notification and authentication endpoints

Central backend uses host port 8002 to avoid conflict with Sharmila's monitoring service on port 8000.

## Verification

Swagger verification completed successfully for:
- Alert creation
- Authentication-protected alert retrieval
- Alert read operation
- Active alerts
- Congestion synchronization
- Analytics trends
- Analytics heatmap
- JSON reports
- CSV report download

Final backend regression suite: 36 tests passed with 1 non-blocking Starlette/httpx deprecation warning.

## Important Integration Note

Sharmila's /analytics/alerts endpoint currently provides historical threshold-breach data from the traffic history dataset. The congestion synchronization endpoint is therefore a controlled polling/synchronization mechanism and should not be described as a true live traffic feed.

## Deployment

Production deployment is not part of M3. Deployment activities are planned for M4.

## M3 Status

Backend and integration work for the assigned M3 scope is complete, subject to final repository review and Team-3 push.
