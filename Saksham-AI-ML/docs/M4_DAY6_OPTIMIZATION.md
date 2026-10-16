# M4 Day 6: Latency Optimization and Defect Handling

## Changes
- Made the alert-service base URL configurable through `ALERT_SERVICE_URL`.
- Prevented alert-service connection failures from crashing the anomaly-detection endpoint.
- Logged alert-delivery failures for troubleshooting.

## Verification
- Python syntax check passed.
- Docker image rebuilt and container restarted.
- Anomaly endpoint tested with road R101, expected level MEDIUM, observed level SEVERE.
- Result: HTTP request succeeded and returned `flagged_as: possible_incident`.

## Limitation
- Successful anomaly detection does not confirm successful alert delivery.
- Alert-service delivery and production deployment remain unverified.
- Latency optimization and accuracy benchmarking remain pending.
