#!/usr/bin/env bash
# ==============================================================================
# TrafficVision AI — Cloud Deployment Smoke Test Suite
# Tests: Health of all microservices via Gateway + Authenticated JWT execution
# ==============================================================================

set -e

BASE_URL="${1:-http://127.0.0.1:8080}"
TEST_EMAIL="${2:-admin@trafficvision.ai}"
TEST_PASSWORD="${3:-Admin@12345}"

echo "=========================================================="
echo "TrafficVision AI — Smoke Test Starting on: $BASE_URL"
echo "=========================================================="

# 1. Gateway Health Probe
echo -n "[1/7] Testing Gateway Health (/health)... "
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
if [ "$HEALTH_CODE" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "FAIL (HTTP $HEALTH_CODE)"
    exit 1
fi

# 2. Database Readiness Probe
echo -n "[2/7] Testing Database Readiness (/ready)... "
READY_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/ready")
if [ "$READY_CODE" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "FAIL (HTTP $READY_CODE)"
    exit 1
fi

# 3. Authenticated Call (Login to receive JWT)
echo -n "[3/7] Testing Authentication (POST /api/v1/auth/login)... "
LOGIN_RESP=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESP" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 || true)

if [ -n "$TOKEN" ]; then
    echo "PASS (JWT Token Acquired)"
else
    echo "FAIL (Could not parse access_token from response: $LOGIN_RESP)"
    exit 1
fi

# 4. Auth Verification (/api/v1/auth/me)
echo -n "[4/7] Testing Token Verification (GET /api/v1/auth/me)... "
ME_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/api/v1/auth/me")
if [ "$ME_CODE" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "FAIL (HTTP $ME_CODE)"
    exit 1
fi

# 5. Route Analysis Service Health via Gateway
echo -n "[5/7] Testing Route Analysis via Gateway (/api/v1/route/conditions?road_id=1)... "
ROUTE_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/api/v1/route/conditions?road_id=1")
if [ "$ROUTE_CODE" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "WARN/FAIL (HTTP $ROUTE_CODE - verify route-analysis container is running)"
fi

# 6. Alert Service Health via Gateway
echo -n "[6/7] Testing Alert Service via Gateway (/api/v1/alerts/active)... "
ALERT_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/api/v1/alerts/active")
if [ "$ALERT_CODE" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "WARN/FAIL (HTTP $ALERT_CODE - verify alert-service container is running)"
fi

# 7. AI Prediction Engine Health via Gateway
echo -n "[7/7] Testing AI Prediction Engine via Gateway (/api/v1/predict/congestion?road_id=1)... "
PREDICT_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/api/v1/predict/congestion?road_id=1")
if [ "$PREDICT_CODE" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "WARN/FAIL (HTTP $PREDICT_CODE - verify ai-engine container is running)"
fi

echo "=========================================================="
echo "Smoke Test Completed for $BASE_URL!"
echo "=========================================================="
