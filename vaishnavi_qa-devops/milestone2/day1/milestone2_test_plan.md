# TrafficVision AI — Milestone 2 QA Test Plan

## 1. Project

TrafficVision AI — Smart Traffic Prediction & Congestion Management System

## 2. Milestone

Milestone 2 — Traffic Prediction & Route Optimization

## 3. QA Owner

Intern 5 — QA, DevOps & Release Engineering

## 4. Testing Objective

The objective is to verify that the new Milestone 2 services and features work correctly and that existing Milestone 1 functionality remains stable.

## 5. Testing Areas

### 5.1 Historical Traffic Data

Test:

- Historical traffic API
- Traffic aggregation API
- Road-condition API
- Valid and invalid road IDs
- Date/time parameters
- Response structure

### 5.2 Traffic Prediction

Test:

- Congestion prediction
- Peak-hour prediction
- Delay estimation
- Required response fields
- Model version
- Confidence value
- Invalid inputs
- Response latency

### 5.3 Route Analysis

Test:

- Route optimization
- Alternate routes
- Travel-time estimation
- Road conditions
- Origin and destination validation
- Route response structure

### 5.4 Maps Integration

Test:

- Map availability
- Route rendering
- Road path information
- Integration between maps and Route Analysis

### 5.5 Frontend

Test:

- Route Analysis screen
- Prediction charts
- Travel-time display
- Road-condition display
- Prediction report download
- Loading and error states

### 5.6 Regression Testing

Re-test:

- Authentication
- RBAC
- Live Traffic Monitoring
- Existing Milestone 1 functionality

### 5.7 Integration Testing

Verify that:

Authentication → Live Traffic → Prediction → Route Analysis → Frontend

works correctly together.

## 6. Testing Methods

The following methods will be used:

- Functional testing
- API testing
- Negative testing
- Integration testing
- Regression testing
- Performance sanity testing
- RBAC testing
- Automated testing using pytest
- Manual API testing using Postman

## 7. Test Environment

Testing will be performed in the local development environment using:

- Python
- FastAPI
- PostgreSQL/TimescaleDB
- Docker Compose
- Postman
- pytest
- GitHub Actions
- Swagger/OpenAPI

## 8. Defect Management

Defects will be recorded with:

- Defect ID
- Feature
- Description
- Severity
- Priority
- Steps to reproduce
- Expected result
- Actual result
- Status

## 9. Exit Criteria

Milestone 2 QA will be considered complete when:

- Critical defects are resolved
- Major functional tests pass
- Integration tests pass
- Milestone 1 regression tests pass
- RBAC checks pass
- Performance sanity checks are completed
- Code-quality checks are completed
- Final QA report is prepared

## 10. Deployment

Production deployment is explicitly out of scope for Milestone 2.
