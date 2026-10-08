# Milestone 2 – Day 2: Time-Series Storage & Historical Data

## Approach

This project uses **indexed PostgreSQL** for local time-series storage instead of adding the TimescaleDB extension. This keeps the Milestone 2 storage compatible with the existing Milestone 1 PostgreSQL database and the schema approved by Intern 1.

## Historical dataset

`src/generate_historical_data.py` creates four complete weeks of hourly simulated traffic history from the existing M1 road profiles.

- Roads: 6 (`R001`–`R006`)
- Period: 4 weeks
- Interval: 1 hour per road
- Records: **4,032**
- Source marker: `simulated_m2_day2`
- Time zone: `+05:30` (IST)

Calculation:

`4 weeks × 7 days × 24 hours × 6 roads = 4,032 records`

The generator includes weekday/weekend differences and morning/evening peaks so the data is suitable as simulated training history.

## Storage

The historical records are stored in `traffic_history` with:

- `TIMESTAMP WITH TIME ZONE`
- FK `road_id -> roads(road_id)`
- indexes on road/time, sensor/time and congestion/time
- covering latest-record index for efficient historical reads

## Commands

From the project root:

```powershell
python src\generate_historical_data.py
```

Then apply the database schema/migration using pgAdmin or `psql`:

```powershell
psql -U postgres -d traffic_monitoring -f database\schema.sql
psql -U postgres -d traffic_monitoring -f sql\m2_day2_timeseries_setup.sql
```

Load the generated data:

```powershell
python src\load_historical_data.py
```

Validate:

```powershell
psql -U postgres -d traffic_monitoring -f tests\validate_m2_day2.sql
```

## Expected validation

```text
Total historical records: 4032
Distinct roads: 6
Distinct sensors: 6
Invalid records: 0
```

The earliest and latest timestamps should cover four complete weeks.

## Scope

This is simulated historical data for Milestone 2 development/training preparation. It is not real sensor data and does not represent a trained ML model.
