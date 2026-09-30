# M3 Day 2 – Congestion Threshold Monitoring

## Objective

Build a threshold-watching workflow that monitors live traffic congestion and informs Intern 1's Alert System when a road crosses the congestion threshold.

## Owner

Intern 2 – Data Engineering & Traffic Monitoring

## Consumer

Intern 1 – Alerts / Backend Integration

## Existing M2 Data Source

The watcher uses the existing live traffic monitoring data from:

`GET /api/v1/traffic/live`

No changes were made to the existing M2 traffic APIs.

## Congestion Threshold

The watcher treats these levels as threshold breaches:

- High
- Severe

The following levels do not trigger alerts:

- Low
- Medium

## Alert Payload

The watcher sends the following fields to Intern 1's Alert System:

- road_id
- congestion_level
- vehicle_count
- traffic_density
- avg_speed_kmph
- timestamp

## Field Mapping

The existing M2 live API may provide:

- `density`
- `updated_at`

The M3 watcher maps these to the agreed alert contract:

- `density` → `traffic_density`
- `updated_at` → `timestamp`

## Monitoring Workflow

1. Read live traffic data.
2. Check the congestion level.
3. Detect High or Severe congestion.
4. Build the congestion alert payload.
5. Send the payload to Intern 1's Alert System.
6. Track roads with an active congestion alert.
7. Prevent duplicate alerts for the same ongoing congestion.
8. Reset the road state when congestion falls below the threshold.

## Duplicate Alert Prevention

If a road remains at High or Severe congestion, repeated live readings do not create duplicate alerts.

Example:

High → Alert Created

High → No duplicate alert

High → No duplicate alert

Low → Alert state reset

High → New alert can be created

## Testing

The automated tests cover:

- High congestion threshold breach
- Severe congestion threshold breach
- Low congestion without alert
- Medium congestion without alert
- Duplicate alert prevention
- Alert state reset after congestion decreases

## Integration Dependency

The watcher is designed to call Intern 1's alert-creation endpoint.

The actual `ALERT_API_URL` must be provided by Intern 1 before end-to-end integration testing.

## Configuration

The following environment variables are used:

`CONGESTION_ALERT_LEVELS=High,Severe`

`ALERT_API_URL=<Intern 1 alert endpoint>`

`ALERT_API_TIMEOUT=5`

## M2 Compatibility

The M3 Day 2 implementation is added as a separate watcher module and does not modify the existing Milestone 2 traffic monitoring APIs, database schema, historical pipeline, aggregation logic, road-condition ingestion, or M2 test files.

## Status

Threshold-watching logic implemented.

Congestion breach detection implemented.

Duplicate alert prevention implemented.

Alert payload contract aligned with Intern 1.

End-to-end alert creation requires Intern 1's actual Alert System endpoint.