# Traffic Data Schema

## Traffic Readings

| Field | Data Type | Description |
|---|---|---|
| reading_id | Integer | Unique ID for each traffic reading |
| road_id | String | Unique identifier of the road |
| sensor_id | String | Unique identifier of the traffic sensor |
| timestamp | DateTime | Time when the traffic reading was recorded |
| vehicle_count | Integer | Number of vehicles detected |
| avg_speed | Float | Average speed of vehicles |
| density | Float | Traffic density |