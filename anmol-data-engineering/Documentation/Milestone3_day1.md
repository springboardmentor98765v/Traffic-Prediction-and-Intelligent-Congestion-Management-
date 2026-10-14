# Milestone 3 – Day 1 Data Plan

## Module

Data Engineering & Traffic Monitoring

## Objective

Review the Milestone 2 data layer and design the Analytics Service
for trend analysis, heatmap aggregation, historical reports, and
the congestion-threshold feed.

---

## 1. Existing Milestone 2 Data Layer

The following existing PostgreSQL structures will be reused:

### traffic_readings

Stores timestamped traffic readings including:

- sensor_id
- timestamp
- vehicle_count
- density
- congestion_level

This table will remain the primary historical time-series source.

### road_conditions

Stores road condition information including:

- road_id
- condition_status
- description
- start_time
- end_time

### hourly_traffic_summary

Provides hourly aggregated traffic information:

- traffic_hour
- sensor_id
- avg_vehicle_count
- avg_density

### daily_traffic_summary

Provides daily aggregated traffic information:

- traffic_date
- sensor_id
- avg_vehicle_count
- avg_density

---

## 2. Analytics Service Design

The Analytics Service will be built on top of the existing Milestone 2
data layer.

### Trend Analysis

Planned endpoint:

GET /analytics/trends

Purpose:

- Provide daily and weekly congestion patterns.
- Use historical traffic data.
- Provide aggregated information for downstream prediction,
  recommendations, and trend visualization.

Planned data source:

- daily_traffic_summary
- traffic_readings when detailed congestion information is required

---

## 3. Heatmap Aggregation

Planned endpoint:

GET /analytics/heatmap

Purpose:

- Aggregate congestion by road and time bucket.
- Produce structured data suitable for frontend heatmap visualization.

Planned dimensions:

- road_id
- time bucket
- congestion information
- aggregated traffic metrics

Primary data source:

- traffic_readings
- road/sensor relationship

---

## 4. Historical Reports

Planned endpoint:

GET /analytics/reports

Purpose:

- Provide historical traffic information in a report-ready format.
- Support CSV-ready output.
- Allow historical data to be consumed by the application/reporting
  layer.

Planned data sources:

- traffic_readings
- hourly_traffic_summary
- daily_traffic_summary

---

## 5. Congestion Threshold Feed

Purpose:

Detect when live congestion crosses a defined threshold and provide
a feed that can be consumed by Intern 1's alert service.

Planned flow:

Live traffic
    ↓
Density / congestion evaluation
    ↓
Threshold breach detection
    ↓
Threshold-breach feed
    ↓
Intern 1 congestion alerts

The threshold logic will be finalized with the alert/integration
requirements before implementation.

---

## 6. Query and Performance Design

The Analytics Service will reuse existing indexes and materialized
views where appropriate.

Existing M2 optimization work includes:

- Historical traffic indexes
- Road/time indexes
- Hourly summary indexes
- Daily summary indexes

Analytics queries will be checked using EXPLAIN ANALYZE during
implementation.

---

## 7. Planned Analytics Components

| Component | Planned Endpoint | Main Data Source |
|---|---|---|
| Trend Analysis | /analytics/trends | daily_traffic_summary / traffic_readings |
| Heatmap | /analytics/heatmap | traffic_readings + road/sensor mapping |
| Historical Reports | /analytics/reports | traffic_readings + summary views |
| Threshold Feed | Internal/API feed | live traffic data |

---

## 8. M3 Data Flow

M2 Data Layer
    ↓
Analytics Service
    ├── Trend Analysis
    ├── Heatmap Aggregation
    └── Historical Reports

Live Traffic
    ↓
Threshold Detection
    ↓
Intern 1 Alert Service

---

## Day 1 Status

- Milestone 2 data layer reviewed
- Analytics Service design prepared
- Trend analysis planned
- Heatmap aggregation planned
- Historical report generation planned
- Congestion-threshold feed planned
- Query/data sources identified

Day 1 deliverable: M3 data plan and Analytics schema/query design.