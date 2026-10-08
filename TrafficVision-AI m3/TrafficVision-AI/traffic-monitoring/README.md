# Traffic Monitoring Service – Day 3

## Overview

The Traffic Monitoring Service provides REST APIs for retrieving live traffic information, road-specific traffic status, and aggregated traffic density metrics.

The service is built using **Python, FastAPI, and PostgreSQL** and is designed to provide traffic data to other components such as the live dashboard, prediction service, and automated testing modules.

---

## Day 3 Objective

Build APIs that allow other parts of the system to ask:

- What is the traffic situation right now?
- What is happening on a specific road?
- What are the overall traffic density metrics?

---

## Technology Stack

| Component         | Technology           |
| ----------------- | -------------------- |
| Backend           | Python               |
| API Framework     | FastAPI              |
| Database          | PostgreSQL           |
| Database Driver   | psycopg2             |
| API Documentation | Swagger / OpenAPI    |
| Server            | Uvicorn              |
| API Testing       | Swagger UI / Postman |
| Automated Testing | pytest               |

---

## Project Structure

```text
traffic_monitoring_day3/
│
├── src/
│   ├── main.py
│   ├── database.py
│   └── traffic_service.py
│
├── tests/
│   └── test_traffic_api.py
│
├── requirements.txt
└── README.md
```
