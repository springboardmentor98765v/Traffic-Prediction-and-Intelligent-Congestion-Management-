# Recommended Milestone 2 Improvements

## 1. Objective
Extend the Milestone 1 monitoring foundation into a real-data, ML-based traffic prediction platform.

## 2. Real Sensor/API Integration
Current:
```text
Synthetic/Historical Data
```

Recommended:
```text
Real Sensor/API
      ↓
Ingestion Adapter
      ↓
Validation / Normalization
      ↓
PostgreSQL + Redis
```

Normalize different external payloads into the internal traffic schema.

## 3. Stable Data Contract
Recommended core fields:
```text
road_id
sensor_id
reading_timestamp
vehicle_count
avg_speed_kmph
density_vehicles_per_km
congestion_level
```

Possible real-data additions:
```text
latitude
longitude
data_source
quality_flag
received_timestamp
```

## 4. Data Validation
Add checks for:
- missing fields
- invalid timestamps
- duplicates
- negative vehicle counts
- negative speeds
- invalid density
- unknown roads
- unknown sensors
- stale sensor readings
- impossible values

## 5. Data Quality Monitoring
Track:
```text
records_received
records_accepted
records_rejected
missing_values
duplicate_records
stale_sensor_readings
```

## 6. Redis Improvements
Continue using Redis for live reads.

Recommended:
```text
TTL for stale data
cache freshness timestamp
sensor heartbeat
latest reading per road
```

Detect stale cache data rather than treating it as current.

## 7. Historical Pipeline
```text
Raw Data
   ↓
Validation
   ↓
Cleaning
   ↓
Feature Engineering
   ↓
Training Dataset
   ↓
Model Training
```

## 8. Feature Engineering
Traffic:
```text
vehicle_count
density_vehicles_per_km
avg_speed_kmph
```

Time:
```text
hour_of_day
day_of_week
is_weekend
is_peak_hour
```

Historical:
```text
lag values
rolling averages
density change
speed change
```

Road:
```text
road_id
road_capacity
road_length_km
```

## 9. ML Prediction
Milestone 1:
```text
Data → Heuristic Rules → Congestion
```

Milestone 2:
```text
Historical Features → Trained ML Model → Prediction
```

Keep the heuristic model as a baseline.

## 10. Prediction API
A future endpoint could be:
```http
GET /api/v1/predictions/road/{road_id}
```

or:
```http
POST /api/v1/predictions
```

Possible response:
```json
{
  "road_id": "R001",
  "prediction": "High",
  "confidence": 0.87,
  "prediction_time": "2026-08-30T20:00:00",
  "horizon_minutes": 15
}
```

Final schema should be agreed with Gateway and dashboard teams.

## 11. Model Evaluation
Recommended:
```text
Accuracy
Precision
Recall
F1-score
Confusion Matrix
```

Compare the trained model against the Milestone 1 heuristic baseline.

## 12. Time-Series Validation
Use chronological splitting:
```text
Earlier → Training
Later   → Validation
Latest  → Test
```

Avoid leakage from future traffic readings.

## 13. Model Versioning
Track:
```text
model version
training date
dataset version
features
algorithm
hyperparameters
metrics
```

## 14. Model Monitoring
After deployment, monitor:
```text
prediction accuracy
prediction latency
data drift
feature drift
class distribution
API errors
```

## 15. Testing Improvements
Extend the existing 20-test baseline with:
- Redis tests
- DB integration tests
- Gateway integration tests
- Prediction API tests
- preprocessing tests
- inference tests
- invalid sensor payload tests
- stale-data tests
- performance tests

## 16. Performance Improvements
Continue using:
```sql
EXPLAIN ANALYZE
```

Potential improvements:
- appropriate composite indexes
- pagination
- time-window filtering
- connection pooling
- Redis caching
- batch ingestion
- async processing where appropriate

## 17. Security
For production:
- JWT/API authentication
- HTTPS
- secret management
- DB access controls
- Redis authentication
- input validation
- rate limiting
- CORS configuration
- audit logging

Never hard-code credentials.

## 18. Observability
Add:
```text
application logs
API latency metrics
DB latency
Redis hit/miss metrics
ingestion metrics
prediction latency
error counts
```

## 19. Recommended Architecture
```text
Real Sensors / Traffic API
          ↓
Traffic Ingestion
          ↓
Validation / Normalization
          ↓
     +----+----+
     |         |
     v         v
PostgreSQL   Redis
     |         |
     +----+----+
          ↓
Traffic Monitoring API
          ↓
      API Gateway
          ↓
   +------+------+
   |             |
   v             v
Prediction    Dashboard
Service
```

## 20. Priority Plan

### Priority 1
- Real sensor/API integration
- Stable data contract
- Validation
- Historical pipeline
- Feature engineering
- Baseline ML model
- Prediction API
- Gateway integration

### Priority 2
- Model evaluation
- Redis freshness/TTL
- Data-quality monitoring
- Integration testing
- Dashboard prediction integration

### Priority 3
- Drift monitoring
- Automated retraining
- Advanced forecasting
- Advanced anomaly detection
- Production observability

## 21. Final Recommendation
Retain the Milestone 1 Traffic Monitoring Service as the monitoring/data foundation.

The main Milestone 2 transition is:

```text
Synthetic/Historical Heuristic Monitoring
                ↓
Real Data + Feature Engineering
                ↓
Trained ML Prediction
                ↓
Prediction API
                ↓
Gateway + Dashboard
```

**Milestone 1 Monitoring Foundation: Completed.**
