# Milestone 2 Historical Traffic Data Schema

## Existing Milestone 1 Structure

The Milestone 1 traffic database uses the `traffic_data`
table with the following traffic fields:

- road_id
- timestamp
- vehicle_count
- density
- congestion_level

## Milestone 2 Historical Schema

The existing traffic fields will be used as the foundation
for historical and time-series traffic storage.

| Field | Description |
|---|---|
| road_id | Identifier of the road or traffic segment |
| timestamp | Time of the traffic observation |
| vehicle_count | Number of vehicles recorded |
| density | Traffic density |
| congestion_level | Congestion classification |

## Intended Usage

The historical traffic data will support:

- Historical traffic analysis
- Traffic trend analysis
- Aggregated traffic metrics
- ML feature preparation
- Congestion prediction
- Peak-hour forecasting
- Delay estimation

## Schema Coordination

The five fields were reviewed with the AI/ML team
(Intern 3) and confirmed to be sufficient for the
Milestone 2 data requirements.