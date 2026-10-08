# M2 Day 4 - Road Condition Data

## Objective

Add road-condition information such as closures, construction, hazards and events so Route Analysis can warn users about affected roads.

## Implementation

The existing M2 PostgreSQL schema already contains the `road_conditions` table. Day 4 adds an ingestion workflow, sample data, an API service function and a FastAPI endpoint.

### Database table

`road_conditions` stores:

- `road_id`
- `condition_timestamp`
- `road_condition`
- `road_status`
- `incident_type`
- `description`
- `source`
- `created_at`

`road_id` is a foreign key to `roads(road_id)`.

### Data ingestion

Input:

`data/road_conditions.csv`

Run:

```powershell
python .\src\road_condition_ingestion.py
```

The loader validates required fields, status values, timestamps, duplicate records and road IDs before inserting the data.

### API

```http
GET /api/v1/traffic/road-condition/{road_id}
```

Example:

```text
http://127.0.0.1:8000/api/v1/traffic/road-condition/R001
```

Response structure:

```json
{
  "road_id": "R001",
  "road_name": "...",
  "count": 2,
  "conditions": [
    {
      "condition_id": 1,
      "road_id": "R001",
      "condition_timestamp": "2026-08-28T08:00:00+05:30",
      "road_condition": "construction",
      "road_status": "Active",
      "incident_type": "construction",
      "description": "Road widening work near the main junction",
      "source": "simulated_m2_day4",
      "created_at": "..."
    }
  ]
}
```

### Integration ownership

The Traffic Monitoring service owns storage and retrieval of road-condition data.

Intern 1 consumes this API from the Route Analysis `/route/conditions` endpoint.

## Acceptance Criteria

- [x] Road-condition data added
- [x] Road-condition schema extension available
- [x] Data ingestion implemented
- [x] Road-condition API implemented
- [x] Swagger endpoint available
- [ ] Tested with Intern 1
