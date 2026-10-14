Traffic Prediction and Intelligent Congestion Management
Milestone 2 — Day 1

1. Introduction

Milestone 2 focuses on preparing historical traffic data for analysis, aggregation, and future traffic prediction.

During Milestone 1, the project established the basic traffic monitoring pipeline. Traffic data can be ingested, processed, stored in PostgreSQL, congestion can be calculated, and traffic information can be accessed through FastAPI services.

Milestone 2 builds on this existing foundation by introducing a structured approach for storing and accessing historical traffic data over a longer period.

The main objective of Day 1 is to review the existing traffic data structure, finalize the historical data storage approach, identify the required historical fields, and plan efficient time-based data access.

2. Day 1 Objectives

The main objectives of Day 1 are:

Review the existing Milestone 1 traffic data pipeline.
Review the current PostgreSQL database structure.
Plan the storage of historical traffic data.
Finalize the historical traffic data schema.
Identify the fields required for historical analysis.
Review the existing time-based indexes.
Define the approach for efficient historical queries.
Prepare the historical data structure for future traffic prediction and analysis.

3. Existing Milestone 1 Pipeline

The existing Milestone 1 pipeline provides the foundation for the historical data pipeline.

The current flow is:

Traffic Dataset
      ↓
traffic_staging
      ↓
PostgreSQL
      ↓
traffic_readings
      ↓
Congestion Calculation
      ↓
Redis Cache
      ↓
FastAPI

The traffic_staging table acts as the initial landing area for incoming traffic data.

After processing, traffic information is stored in the main traffic_readings table.

The processed traffic data can then be accessed through the FastAPI monitoring service.

4. Existing Database Structure

The existing PostgreSQL database contains the following main tables:

roads
sensors
road_capacity
traffic_readings
congestion_history
traffic_staging

Each table has a specific purpose within the traffic monitoring system.

5. Existing Tables
5.1 Roads

The roads table stores information about roads being monitored.

Important fields include:

road_id
road_code
road_name
road_description
created_at
updated_at
5.2 Sensors

The sensors table stores information about traffic sensors.

Important fields include:

sensor_id
road_id
sensor_code
sensor_name
sensor_type
location
status
installed_at

Each sensor is connected to a road using road_id.

The relationship is:

Road
  ↓
Sensor


5.3 Road Capacity

The road_capacity table stores the configured vehicle capacity for roads.

Important fields include:

capacity_id
road_id
vehicle_capacity
effective_from
effective_to

The road capacity is used to calculate the normalized traffic density.

5.4 Traffic Readings

The traffic_readings table is the main table for processed traffic readings.

Important fields include:

reading_id
sensor_id
source_record_id
timestamp
vehicle_count
density
congestion_level
created_at

The table is suitable for historical traffic storage because each traffic reading contains a timestamp.

5.5 Congestion History

The congestion_history table stores changes in congestion conditions over time.

Important fields include:

history_id
road_id
congestion_level
density
recorded_at
created_at

This table provides additional historical information about congestion changes.

5.6 Traffic Staging

The traffic_staging table is used as the initial landing area for incoming traffic data.

It contains traffic-related fields from the incoming source before the data is processed into the main database tables.

The staging approach provides a separate area where incoming data can be validated and processed.

6. Historical Data Storage Approach

For Milestone 2, PostgreSQL will continue to be used as the primary persistent database.

The existing traffic_readings table will be reused for historical traffic data.

A separate duplicate historical traffic table is not required because traffic_readings already stores timestamped traffic records.

The planned storage approach is:

Traffic Data
     ↓
PostgreSQL
     ↓
traffic_readings
     ↓
Historical Traffic Records

This approach avoids unnecessary duplication and keeps the database structure consistent with Milestone 1.

7. Reason for Reusing traffic_readings

The existing traffic_readings table already contains the information required for historical traffic analysis.

Each record includes:

Sensor information
Timestamp
Vehicle count
Density
Congestion level

Because the records are timestamped, the same table can be used to store traffic information over an extended period.

Reusing the table provides the following benefits:

Avoids duplicate traffic data.
Keeps the database design simple.
Reuses the existing Milestone 1 structure.
Maintains consistency across the traffic pipeline.
Makes historical queries easier to manage.
Reduces unnecessary database maintenance.
8. Historical Traffic Data Schema

The main historical traffic information will be stored in the existing traffic_readings table.

The important fields are:

Field	Description
reading_id	Unique identifier for each traffic reading
sensor_id	Identifies the sensor that generated the reading
timestamp	Date and time when the reading was recorded
vehicle_count	Number of vehicles recorded
density	Normalized traffic load
congestion_level	Traffic congestion classification

The existing sensor-to-road relationship provides road information.

traffic_readings
      ↓
   sensor_id
      ↓
   sensors
      ↓
    road_id
      ↓
    roads

Therefore, historical traffic can be analyzed at both sensor and road level.

9. Time-Series Data Design

Traffic data is naturally time-dependent because traffic conditions change throughout the day.

The timestamp field is therefore the main time reference for historical traffic data.

Historical traffic can be queried based on:

Date
Time
Time range
Road
Sensor
Congestion level

Typical historical queries include:

Traffic for a specific date
Traffic between two timestamps
Traffic for a particular road
Traffic for a particular sensor
Latest traffic readings
Traffic patterns over time

This structure allows the database to support historical analysis as the amount of traffic data grows.

10. Existing Time-Based Indexes

The existing database schema already contains indexes for traffic queries.

Timestamp Index
CREATE INDEX IF NOT EXISTS idx_traffic_timestamp
ON traffic_readings(timestamp);

This index helps queries that filter or sort traffic records using timestamps.

Sensor and Timestamp Index
CREATE INDEX IF NOT EXISTS idx_traffic_sensor_timestamp
ON traffic_readings(sensor_id, timestamp);

This index supports queries that retrieve traffic records for a specific sensor using the timestamp.

These indexes provide the initial performance support required for historical queries.

Additional indexing and optimization can be considered later based on actual performance testing.

11. Historical Query Examples
11.1 Retrieve Traffic for a Time Range
SELECT *
FROM traffic_readings
WHERE timestamp BETWEEN %s AND %s
ORDER BY timestamp;

This query retrieves historical traffic records between two timestamps.

11.2 Retrieve Traffic for a Sensor
SELECT *
FROM traffic_readings
WHERE sensor_id = %s
ORDER BY timestamp DESC;

This query retrieves historical traffic readings for a particular sensor.

11.3 Retrieve Recent Traffic Records
SELECT *
FROM traffic_readings
ORDER BY timestamp DESC
LIMIT 50;

This query retrieves the most recent traffic records.

12. Historical Data Requirements

The historical traffic pipeline should maintain the following information:

Road
Sensor
Timestamp
Vehicle Count
Density
Congestion Level

The road information is available through the existing relationship:

Road
  ↓
Sensor
  ↓
Traffic Reading

This structure allows historical traffic data to be grouped and analyzed by:

Road
Sensor
Date
Time
Congestion level
13. Data Quality Requirements

Historical traffic data needs to be reliable before it is used for analysis or prediction.

The following conditions will be considered during the M2 data pipeline.

13.1 Duplicate Records

Duplicate traffic readings should be identified and removed where required.

13.2 Missing Timestamps

Historical readings should contain valid timestamps so that records can be correctly ordered and analyzed.

13.3 Invalid Vehicle Counts

Vehicle counts should not contain negative values.

13.4 Invalid Density

Density values should remain within the valid normalized range:

0 to 1
13.5 Invalid Congestion Levels

The supported congestion levels are:

LOW
MEDIUM
HIGH
SEVERE
13.6 Historical Gaps

Missing periods or gaps in the historical dataset should be identified during the data-cleaning stage.

Detailed cleaning and validation will be implemented during the later stages of Milestone 2.

14. Historical Data and Prediction

Historical traffic data will provide the foundation for future traffic analysis and prediction.

The main information available for future feature engineering includes:

road_id
sensor_id
timestamp
vehicle_count
density
congestion_level

The road_id is obtained through the existing relationship between traffic_readings, sensors, and roads.

These fields can later be used to derive traffic-related and time-based features such as:

Hour of the day
Day of the week
Average traffic
Peak traffic periods
Previous traffic conditions
Traffic trends
Congestion patterns

The actual feature engineering and machine learning model development are outside the scope of Day 1.

The purpose of this stage is to ensure that the historical data is stored in a suitable and consistent structure.

15. Historical Data Flow

The planned historical data flow for Milestone 2 is:

Traffic Source
      ↓
Data Ingestion
      ↓
PostgreSQL
      ↓
traffic_readings
      ↓
Historical Traffic Data
      ↓
Data Cleaning & Validation
      ↓
Historical APIs
      ↓
Traffic Analysis / Prediction

This pipeline allows historical traffic information to move from the source into persistent storage and later be accessed by other services.

16. Relationship Between M1 and M2

Milestone 2 builds on the existing Milestone 1 components.

Milestone 1
Traffic Data
      ↓
PostgreSQL
      ↓
traffic_readings
      ↓
Congestion Calculation
      ↓
Monitoring APIs
Milestone 2
Historical Traffic Data
      ↓
PostgreSQL
      ↓
traffic_readings
      ↓
Historical Queries
      ↓
Historical APIs
      ↓
Traffic Analysis / Prediction

The same database foundation can therefore support both traffic monitoring and historical analysis.

17. Historical Data Access

Historical data will be accessed through the application's API layer.

The planned architecture is:

PostgreSQL
     ↓
Historical Traffic Data
     ↓
FastAPI
     ↓
Historical Traffic APIs
     ↓
Other Project Modules

This keeps database access within the application layer and allows other modules to request historical information through APIs.

Historical API implementation will be completed during the later stage of Milestone 2.

18. Database Performance Considerations

Historical data will increase over time, so efficient database access is important.

The following approach will be followed:

Use timestamp-based indexes.
Use sensor and timestamp indexes for sensor-specific queries.
Filter historical data using appropriate time ranges.
Avoid retrieving unnecessary records.
Use EXPLAIN ANALYZE to study query performance.
Add or improve indexes when performance testing identifies a requirement.

Performance optimization will be implemented during the relevant M2 stage after sufficient historical data is available.

19. Scalability Considerations

The historical traffic dataset is expected to grow as more traffic records are collected.

The current design provides a simple starting point for storing increasing amounts of timestamped traffic data.

The database structure can be further optimized in future stages if the data volume or query requirements increase.

Potential future improvements may include:

Additional time-based indexes.
Query optimization.
Aggregated traffic tables.
Partitioning or specialized time-series storage if required by future scale.

These improvements will be considered based on actual project requirements and performance results.

20. Day 1 Design Decisions

The following decisions have been made for the Milestone 2 historical data design.

Database

PostgreSQL will continue to be used as the primary persistent database.

Historical Storage

The existing traffic_readings table will be reused for historical traffic records.

Time Field

The existing timestamp column will be used as the main time reference for historical traffic data.

Main Historical Information
Sensor
Timestamp
Vehicle Count
Density
Congestion Level
Road Identification

Road information will be obtained through:

Road
  ↓
Sensor
  ↓
Traffic Reading
Query Optimization

The existing timestamp and sensor-timestamp indexes will be used and evaluated during later performance testing.

Data Quality

Historical data will be checked for duplicates, invalid values, missing timestamps, and gaps during the later cleaning stage.

21. Day 1 Deliverables

The Day 1 work covers the following:

Review of the Milestone 1 traffic pipeline.
Review of the existing PostgreSQL database structure.
Historical storage approach finalized.
Existing traffic_readings table selected for historical storage.
Historical traffic fields identified.
Road-sensor-reading relationship reviewed.
Time-series storage approach defined.
Existing timestamp indexes reviewed.
Historical query requirements identified.
Data-quality requirements defined.
Historical data flow documented.
22. Current Status

The historical data design is based on the existing Milestone 1 database structure.

The existing traffic_readings table provides timestamped traffic records and can therefore be reused for historical traffic storage.

The existing relationships between roads, sensors, and traffic readings provide the required road-level identification.

The existing timestamp-related indexes provide a starting point for efficient historical queries.

No separate duplicate historical traffic table is required at this stage.

The database design is therefore ready for the next stage of Milestone 2, where a larger historical dataset will be prepared and loaded.

23. Day 1 Completion Summary

Day 1 establishes the foundation for the Milestone 2 historical data pipeline.

The selected approach is:

Existing Traffic Data
        ↓
PostgreSQL
        ↓
traffic_readings
        ↓
Timestamp-Based Historical Storage
        ↓
Historical Queries
        ↓
Future Historical APIs
        ↓
Traffic Analysis / Prediction

The existing M1 database structure will be reused instead of creating unnecessary duplicate storage.

This provides a simple and consistent foundation for handling historical traffic data in the next stages of Milestone 2.