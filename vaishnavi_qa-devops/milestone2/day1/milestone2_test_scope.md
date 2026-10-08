# TrafficVision AI — Milestone 2 QA Test Scope

## 1. Purpose

The purpose of Milestone 2 QA testing is to validate the new Traffic Prediction and Route Optimization functionality while ensuring that all Milestone 1 features continue to work correctly.

## 2. Scope

The following Milestone 2 features will be tested:

### Traffic Prediction

- Congestion prediction
- Peak-hour forecasting
- Delay estimation
- Real trained prediction model
- Prediction response time

### Historical Traffic Data

- Historical traffic data retrieval
- Traffic aggregation
- Data validation
- Road-condition information

### Route Analysis

- Route optimization
- Alternate-route recommendations
- Travel-time estimation
- Road-condition information

### Maps Integration

- Map loading
- Road/route display
- Route geometry
- Map integration with Route Analysis

### Frontend

- Route Analysis page
- Prediction visualizations
- Travel-time display
- Road-condition display
- Prediction report download

### Integration

- Authentication
- RBAC
- Live Traffic Monitoring
- Prediction Service
- Route Analysis Service
- Frontend
- Docker Compose local environment

## 3. Regression Scope

Milestone 1 features will be re-tested to ensure that Milestone 2 changes do not introduce regressions.

The following will be included:

- Authentication
- RBAC
- Live Traffic Monitoring
- Existing prediction functionality

## 4. Non-Functional Checks

The following will also be checked:

- API response time
- API error handling
- Input validation
- Authorization/RBAC
- Code quality
- Local Docker integration

## 5. Out of Scope

Production deployment is not included in Milestone 2.

All testing will be performed in the local development/integration environment.

## 6. QA Objective

The final objective is to confirm that the Milestone 2 features work correctly, integrate with Milestone 1, and are ready for final QA sign-off.
