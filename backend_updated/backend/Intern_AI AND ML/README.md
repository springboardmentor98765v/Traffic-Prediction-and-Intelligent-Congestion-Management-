## TrafficVision AI API Documentation

### 1. Authentication Endpoints (`/api/v1/auth`)

- `POST /register`: Registers a new user with role-based validation (`admin`, `user`, `operator`).
- `POST /login`: Authenticates user credentials and returns a JWT `access_token`.

### 2. Route Analysis Endpoints (`/api/v1/route`)

- `GET /api/v1/route/alternate`: Requires Bearer token authorization. Takes `origin` and `destination` coordinates (`lat,lng`) and returns ranked alternative paths integrated with ML congestion predictions.

During this milestone, we successfully designed, built, and integrated the core backend architecture and machine learning pipeline for the TrafficVision AI system.

Key Deliverables & Architecture:

FastAPI Backend & Routing: Developed scalable RESTful endpoints for user authentication, route analysis, and predictive metrics.

Database & ORM: Integrated PostgreSQL with SQLAlchemy for reliable data persistence, handling user records, historical metrics, and road conditions.

Security & RBAC: Implemented secure JWT authentication and Role-Based Access Control (RBAC) with strict Pydantic Enum input validation to prevent unauthorized access and malformed requests.

Machine Learning Integration: Embedded a Scikit-learn classification pipeline (model-v1.joblib) to dynamically evaluate congestion levels, delays, and alternate routes indexed by unique road_id keys.

Cross-Team Integration: Successfully synchronized endpoints with Data Engineering and Predictive services (Interns 1, 2, and 3) to ensure seamless data flow from live traffic inputs to route optimization outputs.

QA & Testing: Validated full end-to-end user journeys via Swagger UI, ensuring robust error handling (e.g., graceful 400 Bad Request and 422 Unprocessable Entity responses).
