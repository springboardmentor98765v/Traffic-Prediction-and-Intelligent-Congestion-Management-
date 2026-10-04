# TrafficVision M4 Backend Handoff Notes

## Handoff From
Gargi - Backend & Integration

## M3 Backend Baseline

The Team-3 backend is running locally on:

http://localhost:8002

Swagger:

http://localhost:8002/docs

PostgreSQL database:

trafficvision

## Current Services / Ports

- Central backend: 8002
- Sharmila traffic monitoring service: 8000
- Manasa AI service: 8001
- Samruddhi frontend: 3000

The central backend uses port 8002 to avoid the port conflict with Sharmila's service on port 8000.

## M3 Backend Components Completed

### Alerts
- Alert creation
- Role-scoped alert recipients
- My alerts endpoint
- Mark-alert-as-read
- Active alerts
- Congestion synchronization
- Delay alert generation
- Road closure alert generation

### Analytics
- Trends endpoint
- Heatmap endpoint
- JSON historical reports
- CSV historical report download

### Integration
- Sharmila congestion threshold feed synchronization
- Manasa AI anomaly alert integration
- Frontend authentication endpoint updated to central backend
- Frontend traffic data endpoint updated to central backend
- Frontend notification endpoints updated to central backend
- Near-real-time notification polling implemented in frontend

## Database

Alert recipient table:

alert_recipients

This table provides per-user alert read state and role-scoped delivery.

Current central roads:
- Road 1: Anna Salai
- Road 2: Mount Road
- Road 3: GST Road

Sharmila's historical alert feed also contains Road 4 records. These are skipped by the central alert service because Road 4 does not currently exist in the central roads table.

## Known Integration Dependency

Manasa's AI project currently has a local model-path dependency:

The prediction service expects:

m2_traffic_model.pkl

The inspected AI project currently contains:

src/traffic_model.pkl

Manasa reported that her E2E test successfully produced possible_incident alerts through the central Alert Service. Therefore the AI-to-alert flow has been verified in her environment, but local startup of the AI service may require the model-path mismatch to be corrected by the AI owner.

Do not rename or modify Manasa's model files from the backend repository without coordination.

## Historical Feed Note

Sharmila's /analytics/alerts endpoint currently reads historical traffic data. It contains threshold breaches from the available historical dataset.

The central /alerts/sync/congestion endpoint should therefore be treated as a controlled synchronization/polling operation, not as a true real-time traffic feed.

## M4 Recommended Backend Tasks

1. Review M3 integration after all services are started together.
2. Validate the final AI service model path with the AI owner.
3. Re-run end-to-end alert flow after the final AI service is available.
4. Perform deployment preparation and environment configuration.
5. Review secrets and production configuration.
6. Validate production CORS and service URLs.
7. Review database migration strategy for deployment.
8. Run final regression and integration tests before deployment.
9. Prepare deployment documentation and rollback procedure.

## Deployment Boundary

Production deployment was intentionally not performed during M3.

Deployment and production-readiness activities belong to M4.

## Final Handoff

The M3 backend API and integration baseline is ready for continued M4 work on Team-3.
