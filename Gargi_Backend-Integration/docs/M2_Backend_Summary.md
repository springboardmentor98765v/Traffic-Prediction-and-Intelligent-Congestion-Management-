# TrafficVision AI — Milestone 2 Backend Summary

## 1. Milestone Overview

Milestone 2 focused on extending the TrafficVision AI backend from the Milestone 1 traffic monitoring foundation into an integrated traffic prediction and route analysis platform.

The backend was extended with trained congestion prediction, historical traffic analysis, peak-hour and delay prediction, route optimization, alternate-route analysis, travel-time estimation, road-condition monitoring, maps integration, API gateway routing, role-based access control, rate limiting, automated testing, and Docker-based deployment support.

---

## 2. M2 Objectives

The major objectives completed during Milestone 2 were:

* Integrate a trained congestion prediction model.
* Provide historical traffic and traffic aggregation APIs.
* Add peak-hour prediction and delay estimation.
* Integrate a free maps/routing service.
* Implement Route Analysis APIs.
* Provide optimized and alternate route analysis.
* Add travel-time estimation and road-condition APIs.
* Integrate Route Analysis with the API gateway.
* Extend authentication, RBAC, and rate limiting.
* Validate integration through automated API tests.
* Provide Docker-based backend and PostgreSQL execution.
* Maintain API documentation through FastAPI OpenAPI/Swagger.

---

## 3. Backend Architecture

The backend follows a modular FastAPI architecture.

```text
Client
   |
   v
FastAPI API Gateway
   |
   +-------------------+
   |                   |
   v                   v
Authentication      Traffic APIs
   |                   |
   +---------+---------+
             |
             v
       Prediction APIs
             |
             v
      Route Analysis APIs
             |
       +-----+-----+
       |           |
       v           v
   Maps Service  Traffic Data
       |           |
       v           v
      OSRM      PostgreSQL
```

The application is organized into independent modules for authentication, traffic, prediction, route analysis, database management, and core backend services.

---

## 4. Authentication and RBAC

The authentication system was retained and extended for M2 integration.

Implemented functionality includes:

* User registration.
* User login.
* JWT access tokens.
* Refresh tokens.
* Current-user endpoint.
* Role-based authorization.
* Protected traffic-recording operations.
* Operator/admin access control.

Supported roles:

```text
admin
operator
public
```

Traffic recording requires an authorized `admin` or `operator` role, while public users are prevented from modifying traffic records.

---

## 5. Traffic Monitoring APIs

The traffic module provides historical and aggregated traffic information.

Implemented endpoints:

```text
GET  /api/v1/traffic/history
GET  /api/v1/traffic/aggregate
POST /api/v1/traffic/record
```

The traffic data model stores:

* Road ID
* Vehicle count
* Traffic density
* Congestion level
* Recording timestamp

Aggregation supports different time granularities including hourly and daily analysis.

---

## 6. AI Congestion Prediction

The previous heuristic prediction approach was replaced with a trained machine-learning model.

The trained model is stored at:

```text
ml/models/congestion_model.joblib
```

The prediction service uses traffic-related features including:

* Road ID
* Hour
* Day of week
* Vehicle count
* Traffic density

The deployed model version is:

```text
random-forest-v1
```

Implemented prediction endpoints:

```text
GET /api/v1/predict/congestion
GET /api/v1/predict/peak-hours
GET /api/v1/predict/delay
```

The congestion endpoint returns:

* Road ID
* Predicted congestion level
* Confidence
* Model version

---

## 7. Peak-Hour Prediction

The peak-hour service analyses historical traffic density to identify periods of elevated congestion.

The endpoint:

```text
GET /api/v1/predict/peak-hours
```

returns predicted peak windows for a specified road.

This provides a foundation for future congestion-aware route planning and traffic recommendations.

---

## 8. Delay Prediction

The delay prediction endpoint estimates expected travel delay using current traffic conditions and congestion information.

Endpoint:

```text
GET /api/v1/predict/delay
```

The response contains:

* Road ID
* Estimated delay in minutes
* Prediction confidence

---

## 9. Route Analysis Service

A dedicated Route Analysis module was introduced during M2.

The module contains:

```text
app/route/
├── __init__.py
├── maps.py
├── ranking.py
├── router.py
├── schemas.py
├── service.py
├── storage.py
└── conditions.py
```

The Route Analysis Service provides four primary capabilities:

1. Route optimization.
2. Alternate-route generation.
3. Travel-time estimation.
4. Road-condition lookup.

---

## 10. Maps and Routing Integration

A free external routing service was integrated through an internal maps wrapper.

The backend uses:

```text
OpenStreetMap ecosystem
        +
OSRM routing service
```

The maps integration is isolated inside:

```text
app/route/maps.py
```

This abstraction prevents the rest of the application from depending directly on the external routing provider.

The design also allows the maps provider to be replaced or extended in the future.

---

## 11. Route Optimization

Implemented endpoint:

```text
GET /api/v1/route/optimize
```

The endpoint accepts an origin and destination and obtains routing information through the maps service.

The response includes:

* Route ID
* Route path
* Distance
* Estimated duration
* Congestion score

---

## 12. Alternate Routes

Implemented endpoint:

```text
GET /api/v1/route/alternate
```

The service requests alternative routes from the maps provider and ranks them using route and traffic information.

The ranking mechanism considers:

* Route duration.
* Route distance.
* Traffic density.
* Congestion score.

Each alternate route receives a rank to support congestion-aware route selection.

---

## 13. Travel-Time Estimation

Implemented endpoint:

```text
GET /api/v1/route/travel-time
```

The service calculates an estimated travel time using the stored route information and congestion score.

The response identifies that the estimate is based on:

```text
live+predicted
```

This establishes the foundation for more advanced prediction-driven travel-time estimation in later milestones.

---

## 14. Road Conditions

Implemented endpoint:

```text
GET /api/v1/route/conditions
```

Road conditions are stored in PostgreSQL and include:

* Road ID
* Current condition status
* Notes
* Last updated timestamp

Example condition states include:

```text
NORMAL
CONGESTED
CLEAR
```

---

## 15. API Gateway Integration

All backend modules are exposed through the FastAPI application and versioned under:

```text
/api/v1
```

Current M2 API groups include:

```text
/api/v1/auth
/api/v1/traffic
/api/v1/predict
/api/v1/route
```

This provides a consistent entry point for frontend and external clients.

---

## 16. Rate Limiting

A development-level rate limiter was implemented at the application gateway.

Current configuration:

```text
60 requests
per 60 seconds
per client IP
```

The rate limiter protects application endpoints while excluding basic infrastructure endpoints such as:

```text
/
 /health
 /docs
 /openapi.json
 /redoc
```

---

## 17. Database

PostgreSQL is used as the primary relational database for the Dockerized backend.

Core entities include:

```text
roles
users
sessions
roads
traffic_records
road_conditions
```

SQLAlchemy is used as the ORM layer.

The database is automatically initialized through the application's SQLAlchemy metadata configuration.

---

## 18. Docker Integration

The backend was containerized using Docker.

Main services:

```text
trafficvision-backend
trafficvision-postgres
```

The Docker environment uses:

```text
Python 3.12
FastAPI
Uvicorn
PostgreSQL 16
```

Docker Compose manages the backend and PostgreSQL services.

The backend container exposes:

```text
8000
```

PostgreSQL exposes:

```text
5432
```

The Docker image also configures:

```text
PYTHONPATH=/app
```

so that the application and test modules resolve correctly inside the container.

---

## 19. Automated Testing

A dedicated M2 API test suite was implemented.

The test suite contains:

```text
23 tests
```

Coverage includes:

* Root endpoint.
* Health endpoint.
* Authentication.
* Current-user endpoint.
* Authentication enforcement.
* RBAC.
* Traffic recording.
* Historical traffic.
* Traffic aggregation.
* Invalid traffic parameters.
* Congestion prediction.
* Unknown-road handling.
* Peak-hour prediction.
* Delay prediction.
* Route optimization.
* Alternate routes.
* Travel-time estimation.
* Unknown route handling.
* Road conditions.
* Unknown road-condition handling.
* OpenAPI M2 endpoint registration.

Final Docker test result:

```text
23 passed
```

---

## 20. Code Quality Validation

The backend was validated using:

### Black

```text
33 files checked
No files require reformatting
```

### Flake8

```text
No linting errors
```

### Pytest

```text
23 passed
```

### Docker

```text
Docker image built successfully
Backend container started successfully
PostgreSQL container started successfully
Docker test suite: 23 passed
```

---

## 21. Final QA Result

Final Docker verification:

```text
=============================
23 passed, 3 warnings
in 12.22 seconds
=============================
```

The remaining warnings originate from third-party dependencies:

* Starlette/httpx compatibility deprecation.
* AnyIO API deprecation.
* Passlib `crypt` deprecation.

No application-level `datetime.utcnow()` warnings remain.

These dependency warnings are non-blocking and do not affect the successful execution of the M2 API test suite.

---

## 22. API Documentation

FastAPI automatically exposes the backend API documentation through:

```text
/docs
```

OpenAPI specification:

```text
/openapi.json
```

Alternative documentation interface:

```text
/redoc
```

The automated test suite verifies that all required M2 endpoints are registered in the OpenAPI specification.

---

## 23. M2 Deliverables Completed

The following M2 backend deliverables were completed:

* M2 backend architecture extension.
* Route Analysis Service.
* Maps/routing wrapper.
* OSRM integration.
* Route optimization.
* Alternate route analysis.
* Travel-time estimation.
* Road-condition API.
* Congestion prediction integration.
* Peak-hour prediction.
* Delay prediction.
* API gateway integration.
* RBAC protection.
* Rate limiting.
* PostgreSQL integration.
* Docker Compose integration.
* Automated API test suite.
* OpenAPI documentation.
* Code formatting and lint validation.
* Docker-based QA verification.

---

## 24. Known Non-Blocking Limitations

The following items remain suitable for future milestones:

* External routing provider can be replaced with another provider if required.
* Route storage is currently in-memory and can be migrated to persistent storage.
* Congestion-aware ranking can be further enhanced with the production prediction service.
* Rate limiting is currently in-memory and suitable for a single-instance development environment.
* Dependency deprecation warnings should be addressed during future dependency upgrades.
* Production deployment, secrets management, monitoring, and horizontal scaling are outside the current M2 scope.

---

## 25. Milestone Status

```text
Day 1 — Backend review and M2 API planning       COMPLETE
Day 2 — Maps wrapper and Route service           COMPLETE
Day 3 — Optimize and Alternate routes           COMPLETE
Day 4 — Travel Time, Conditions and Gateway      COMPLETE
Day 5 — Prediction and congestion integration    COMPLETE
Day 6 — E2E QA and OpenAPI validation            COMPLETE
Day 7 — Code freeze and handoff                  IN PROGRESS
```

---

## 26. Conclusion

Milestone 2 successfully extends the TrafficVision AI backend from basic traffic monitoring into an integrated traffic prediction and intelligent route analysis platform.

The backend now combines traffic data, machine-learning predictions, routing information, congestion scoring, road conditions, authentication, RBAC, rate limiting, PostgreSQL, and Docker into a modular FastAPI architecture.

The final automated QA run achieved 23/23 passing tests in the Docker environment, confirming that the implemented M2 backend functionality is stable and ready for code freeze and handoff to the next milestone.
