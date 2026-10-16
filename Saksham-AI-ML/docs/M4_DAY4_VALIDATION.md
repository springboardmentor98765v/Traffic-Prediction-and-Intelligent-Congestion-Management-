# M4 Day 4 - Validation Report

## Test Environment
Local Docker AI Engine, port 8001.

## Endpoint Results

| Endpoint | HTTP Status | Latency | Result |
|---|---:|---:|---|
| Prediction | 200 | 93 ms | Pass |
| Anomaly Detection | 500 | 33 ms | Fail |
| AI Recommendations | 200 | 259 ms | Pass |
| Swagger Docs | 200 | 103 ms | Pass |

## Recommendation Response
For road R101 with density 0.8 and vehicle count 100, the API
returned predicted congestion level HIGH and estimated delay of
20.9 minutes. Historical trend data was unavailable.

## Blockers and Limitations
- Anomaly endpoint fails because the Alert Service is unreachable
  at 127.0.0.1:8003; its container exits because the psycopg package
  is missing.
- Latency values are single local requests, not a load test.
- Model accuracy has not been measured in this validation.
- Production cloud deployment has not been verified.

## Conclusion
Prediction and recommendation endpoints responded successfully
in the local Docker environment. Anomaly integration remains blocked.
