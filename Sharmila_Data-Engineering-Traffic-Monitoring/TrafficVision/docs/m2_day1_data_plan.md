# Milestone 2 Data Plan

## 1. Objective

Extend the Milestone 1 traffic data pipeline to support
historical traffic storage and time-based analysis.

## 2. Existing Milestone 1 Data

The existing traffic dataset contains:

- DateTime
- Junction
- Vehicles
- ID

## 3. Milestone 2 Historical Data

The historical traffic store will maintain:

- road_id
- timestamp
- vehicle_count
- density
- congestion_level

## 4. Storage

Historical traffic readings will be stored using a
PostgreSQL-based time-series-friendly structure.

Time-based indexing will be considered for efficient
historical traffic queries.

## 5. Data Processing

The pipeline will support:

- Historical data storage
- Data validation
- Hourly aggregation
- Daily aggregation
- Traffic trend analysis
- ML feature preparation

## 6. Data Usage

The historical data will support:

- Traffic prediction
- Peak-hour forecasting
- Delay estimation
- Route analysis

## 7. API Integration

The historical traffic data will be exposed through
the required traffic history and aggregation APIs.

The Prediction Service will consume historical traffic
data for feature engineering and model training.

## 8. Day 2 Plan

The next step is to configure the PostgreSQL historical
storage structure and generate a multi-week simulated
historical dataset for testing.

## 9. Milestone 2 Day 2 and Day 3 Implementation

### Day 2

- Created the `traffic_history` PostgreSQL table.
- Added timestamp-based indexing.
- Added road and timestamp indexing.
- Generated a four-week simulated historical traffic dataset.
- Generated 2,688 records across 4 roads.
- Loaded the historical dataset into PostgreSQL.

### Day 3

- Implemented `GET /traffic/history`.
- Implemented `GET /traffic/aggregate`.
- Validated the historical dataset.
- Checked for duplicate road and timestamp records.
- Checked for NULL values.
- Checked for invalid traffic values.
- Checked for hourly gaps.
- Created `traffic_history_clean.csv` for ML feature engineering.

## 10. Milestone 2 Day 4 Implementation

### Road-Condition Data Ingestion

A separate `road_conditions` table was created in PostgreSQL
to store road-condition information.

The schema contains:

- id
- road_id
- condition_type
- description
- is_active
- updated_at

### Supported Conditions

The implementation supports:

- Road closures
- Construction
- Road hazards

### API

The following endpoint was implemented:

`GET /traffic/road-condition/{road_id}`

The API retrieves the road-condition records for a
specific road.

### Testing

The API was tested for roads 1, 2, 3, and 4.

The tests confirmed that closure, construction, hazard,
and inactive-condition records are returned correctly.

## 11. Milestone 2 Day 5 Implementation

### Aggregated Traffic Metrics

The historical traffic data was aggregated at two levels:

- Hourly averages per road
- Daily averages per road

The `/traffic/aggregate` API supports both aggregation levels
using the `interval` parameter.

### Query Performance Optimization

The following indexes are available on `traffic_history`:

- `idx_traffic_history_timestamp`
- `idx_traffic_history_road_timestamp`

The `road_id + timestamp` index is used by the historical
aggregation queries.

### Performance Verification

The aggregation queries were tested using PostgreSQL
`EXPLAIN ANALYZE`.

#### Hourly Aggregation

- Planning Time: 0.582 ms
- Execution Time: 5.061 ms
- Index used: `idx_traffic_history_road_timestamp`

#### Daily Aggregation

- Planning Time: 0.356 ms
- Execution Time: 2.128 ms
- Index used: `idx_traffic_history_road_timestamp`

The query execution plans confirmed that the time-series
queries are using the available indexes.

## 12. Milestone 2 Day 6 Testing

Automated tests were added for the historical traffic APIs,
aggregation APIs, road-condition API, and cleaned historical
dataset.

The complete test suite was executed using pytest.

Test result:

- 11 tests passed
- 0 tests failed

The tests verified:

- Historical traffic API response
- Hourly aggregation API
- Daily aggregation API
- Road-condition API
- Clean historical dataset
- Existing Milestone 1 APIs

Database query performance was also reviewed using
PostgreSQL EXPLAIN ANALYZE. The road_id and timestamp index
was confirmed to be used by the historical aggregation
queries.