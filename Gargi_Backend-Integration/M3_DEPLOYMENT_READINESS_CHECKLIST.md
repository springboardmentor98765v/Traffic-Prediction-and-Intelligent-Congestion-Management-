# TrafficVision M4 Deployment Readiness Checklist

## Purpose

This checklist defines the deployment-readiness activities planned for Milestone 4.

No production deployment was performed during Milestone 3.

## Current M3 Service Baseline

- Central Backend: port 8002
- PostgreSQL: port 5432
- Sharmila Traffic Monitoring: port 8000
- Manasa AI Service: port 8001
- Samruddhi Frontend: port 3000

## M4 Readiness Checklist

### 1. Application Configuration
- [ ] Replace development JWT secret with a secure production secret.
- [ ] Configure production database connection.
- [ ] Configure production service URLs.
- [ ] Configure production frontend API URL.
- [ ] Review CORS allowed origins.
- [ ] Review application debug settings.

### 2. Database
- [ ] Review database schema and migrations.
- [ ] Verify all required tables and indexes.
- [ ] Verify alert_recipients migration.
- [ ] Plan database backup and restore procedure.
- [ ] Validate production database connectivity.

### 3. AI Service
- [ ] Confirm the final AI model filename and path with the AI owner.
- [ ] Resolve the current m2_traffic_model.pkl / traffic_model.pkl path dependency.
- [ ] Verify anomaly detection endpoint.
- [ ] Verify AI recommendation endpoint.
- [ ] Verify AI-to-Alert Service integration.

### 4. Backend APIs
- [ ] Run full regression tests.
- [ ] Run integration tests.
- [ ] Verify authentication and RBAC.
- [ ] Verify alert creation and delivery.
- [ ] Verify congestion, accident, closure and delay alerts.
- [ ] Verify analytics endpoints.
- [ ] Verify JSON and CSV report generation.
- [ ] Verify API documentation.

### 5. Frontend
- [ ] Verify login against the production backend URL.
- [ ] Verify notification bell and unread counts.
- [ ] Verify mark-as-read functionality.
- [ ] Verify analytics dashboard.
- [ ] Verify AI recommendation display.
- [ ] Verify report download.
- [ ] Test responsive/mobile behavior.

### 6. Service Integration
- [ ] Verify all services can run together in the final deployment environment.
- [ ] Verify service-to-service communication.
- [ ] Verify database connectivity.
- [ ] Verify frontend-to-backend communication.
- [ ] Verify AI-to-alert communication.
- [ ] Verify traffic-monitoring-to-alert synchronization.

### 7. Security
- [ ] Remove development secrets from deployment configuration.
- [ ] Configure secure JWT secrets.
- [ ] Review authentication and authorization.
- [ ] Review rate limiting.
- [ ] Restrict production CORS origins.
- [ ] Verify sensitive configuration is provided through environment variables.

### 8. Monitoring and Operations
- [ ] Configure application logging.
- [ ] Configure service health checks.
- [ ] Define error monitoring procedure.
- [ ] Define service restart procedure.
- [ ] Define database backup procedure.

### 9. Deployment and Rollback
- [ ] Build final Docker images.
- [ ] Review deployment configuration.
- [ ] Perform final smoke tests.
- [ ] Document deployment steps.
- [ ] Document rollback steps.
- [ ] Confirm deployment approval before production release.

## Known M3 Integration Notes

- The central backend uses port 8002 to avoid conflict with Sharmila's service on port 8000.
- Sharmila's congestion alert endpoint currently uses historical traffic data and should not be described as a true live traffic feed.
- Sharmila's historical feed contains Road 4 records, while the central database currently contains Roads 1-3; unsupported Road 4 alerts are skipped.
- Manasa reported successful AI anomaly-to-alert end-to-end testing, but local AI startup currently depends on resolving the model-path mismatch.
- The actual Team-3 working team has four active interns; there is no Intern 5/QA owner.

## M3 Boundary

Production deployment is intentionally excluded from Milestone 3.

Deployment, production configuration, security hardening, final environment validation and rollback preparation belong to Milestone 4.
