# Milestone 2 – Module Notes

## Module
Data Engineering & Traffic Monitoring

## Responsibilities

- Historical Data Pipeline
- Time-Series Storage
- Road Conditions
- Hourly/Daily Traffic Aggregation
- Query Optimization
- Automated Checks

---

## Day 1 – Historical Time-Series Storage

The existing PostgreSQL `traffic_readings` table was reused for
historical time-series storage.

A separate historical traffic table was not created because the existing
`traffic_readings` table already supports timestamp-based historical
storage.

### Storage Design

- Database: PostgreSQL
- Table: `traffic_readings`
- Historical records are identified using `timestamp`
- Road information is obtained through the relationship between
  `traffic_readings`, `sensors`, and `roads`

---

## Day 2 – Historical Traffic Data

Historical/sample traffic data was loaded into PostgreSQL.

The data is available for historical traffic analysis based on road,
sensor, and timestamp.

---

## Day 3 – Historical Traffic API & Data Quality

The historical traffic API was implemented:

`GET /traffic/history/{road_id}`

The API retrieves historical traffic readings for a specific road.

### API Response

The response contains:

- `reading_id`
- `road_id`
- `sensor_id`
- `timestamp`
- `vehicle_count`
- `density`
- `congestion_level`

### Data Quality Checks

The historical data was checked for:

- Duplicate source records
- Missing timestamps
- Invalid vehicle counts
- Invalid density values
- Invalid congestion levels

The required data quality checks completed successfully.

---

## Day 4 – Road Conditions

A `road_conditions` table was added to store road-condition information.

### Supported Conditions

- `OPEN`
- `CONSTRUCTION`
- `CLOSED`

### Road Condition API

`GET /traffic/conditions/{road_id}`

The API returns:

- `condition_id`
- `road_id`
- `condition_status`
- `description`
- `start_time`
- `end_time`
- `created_at`

The endpoint was tested successfully.

---

## Day 5 – Traffic Aggregation & Query Optimization

Materialized views were created for summarized traffic data.

### Hourly Traffic Summary

`hourly_traffic_summary`

Contains:

- Traffic hour
- Sensor
- Average vehicle count
- Average density

### Daily Traffic Summary

`daily_traffic_summary`

Contains:

- Traffic date
- Sensor
- Average vehicle count
- Average density

### Query Optimization

Indexes were added for frequently used summary lookups.

Query performance was checked using `EXPLAIN ANALYZE`.

Hourly congestion-level aggregation was also verified successfully.

---

## Day 6 – Automated Checks

Automated tests were added to verify the completed functionality.

### Tests Covered

1. LOW congestion classification
2. MEDIUM congestion classification
3. HIGH congestion classification
4. SEVERE congestion classification
5. Historical traffic API
6. Road-condition API

### Final Test Result

`6 passed in 0.71s`

All automated tests passed successfully.

---

## Day 7 – Final Integration

The completed Data Engineering & Traffic Monitoring modules are ready
for final integration testing with the complete project team.

The integration check will cover:

- Historical traffic data
- Historical traffic API
- Road-condition API
- Traffic aggregation
- Database integration