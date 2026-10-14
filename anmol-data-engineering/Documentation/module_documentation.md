# Traffic Monitoring Module

## Overview

The Traffic Monitoring module manages traffic data, road information,
sensor information, road capacity, traffic readings, and congestion history.

## Database Tables

### roads
Stores road information.

- road_id
- road_code
- road_name
- road_description

### sensors
Stores traffic sensor information.

- sensor_id
- road_id
- sensor_code
- sensor_name
- sensor_type
- location
- status

### road_capacity
Stores the vehicle capacity of each road.

- capacity_id
- road_id
- vehicle_capacity
- effective_from
- effective_to

Only one active capacity record is allowed for a road.

### traffic_readings
Stores traffic observations received from sensors.

- reading_id
- sensor_id
- source_record_id
- timestamp
- vehicle_count
- density
- congestion_level

### congestion_history
Stores historical congestion information.

- history_id
- road_id
- congestion_level
- density
- recorded_at

### traffic_staging
Temporary/raw landing table used for incoming traffic data before
it is processed into the main database tables.

## Data Flow

Raw traffic data
        ↓
traffic_staging
        ↓
roads + sensors
        ↓
traffic_readings
        ↓
congestion calculation/history
        ↓
API / Gateway
        ↓
Prediction Service

## Congestion Levels

The system supports four congestion levels:

- LOW
- MEDIUM
- HIGH
- SEVERE

## Data Used for Prediction

Intern 3 can use the following historical fields:

- road_id
- sensor_id
- timestamp
- vehicle_count
- density
- congestion_level
- historical congestion records
- road capacity

These fields can be used to build congestion prediction features
for Milestone 2.

## Database Optimization

The following indexes are used:

- traffic_readings(timestamp)
- traffic_readings(sensor_id, timestamp)
- congestion_history(road_id, recorded_at)

A partial unique index prevents multiple active road-capacity
records for the same road.

## Testing

Database tests verify:

- staging data
- roads
- sensors
- traffic readings
- road capacity
- road utilization
- congestion history
- query performance
- database/table availability

## Milestone 2 Handover

For Milestone 2, the module is ready to provide historical traffic
data to the prediction service.

The prediction module can use traffic readings and congestion
history to generate future congestion predictions.

Further integration should connect the prediction output back to
the API/Gateway for consumption by the frontend and other services.