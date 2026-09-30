#!/usr/bin/env bash
# One-time setup of Intern 2's Analytics tables + 4-week dataset in the shared
# dev DB. Safe to re-run: DDL is IF NOT EXISTS and data loads only when empty.
#
#   docker compose -f docker-compose.dev.yml up -d
#   bash QA/milestone3/day6/analytics_setup.sh
set -euo pipefail

PG=trafficvision-postgres-dev
AN=trafficvision-analytics-dev
DB_USER=${POSTGRES_USER:-traffic}
DB_NAME=${POSTGRES_DB:-trafficvision}
DATA_DIR="$(cd "$(dirname "$0")/../../../Data/M3_Day6_Traffic_Monitoring_" && pwd)"

psql_file() {
  echo "-- applying $1"
  docker exec -i "$PG" psql -q -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" < "$DATA_DIR/$1"
}
scalar() {
  docker exec "$PG" psql -tA -U "$DB_USER" -d "$DB_NAME" -c "$1"
}

psql_file sql/milestone_2_schema.sql
psql_file sql/m2_day5_aggregation.sql
psql_file sql/m3_day5_analytics_optimization.sql

if [ "$(scalar 'SELECT count(*) FROM traffic_history')" = "0" ]; then
  docker exec -w /app "$AN" python src/load_historical_data.py
else
  echo "-- traffic_history already loaded, skipping"
fi

if [ "$(scalar 'SELECT count(*) FROM hourly_traffic_metrics')" = "0" ]; then
  docker exec -w /app "$AN" python src/generate_traffic_aggregates.py
else
  echo "-- aggregates already generated, skipping"
fi

docker exec "$PG" psql -U "$DB_USER" -d "$DB_NAME" -c "ANALYZE traffic_history;" >/dev/null
echo "traffic_history rows: $(scalar 'SELECT count(*) FROM traffic_history')"
echo "hourly_traffic_metrics rows: $(scalar 'SELECT count(*) FROM hourly_traffic_metrics')"
echo "daily_traffic_metrics rows: $(scalar 'SELECT count(*) FROM daily_traffic_metrics')"
