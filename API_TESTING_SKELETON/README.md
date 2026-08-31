# API TESTING SKELETON

## Project
TrafficVision AI — Milestone 1

## Purpose
This is the basic API automation structure for Day 3. Detailed API execution and expansion are performed after the Authentication and Traffic Monitoring services are available.

## Tool
pytest

## Suggested Structure

```text
api_tests/
├── README.md
├── requirements-test.txt
├── conftest.py
├── test_auth.py
└── test_traffic.py
```

## Run

From this directory:

```bash
pip install -r requirements-test.txt
pytest -q
```

## Configuration

Set the API base URL through an environment variable:

```text
TRAFFICVISION_API_URL=http://localhost:8000
```

Do not hard-code production credentials or secrets.

## Day 3 Boundary

This skeleton prepares the framework. Detailed API assertions and complete execution are added when the actual endpoints are available.
