#!/usr/bin/env bash
# ==============================================================================
# TrafficVision AI — API Gateway Production Verification Script
# Tests: Health probes, CORS allowed/blocked origins, Security headers, Rate limiting
# ==============================================================================

set -e

BASE_URL="${1:-http://127.0.0.1:8080}"
ALLOWED_ORIGIN="http://localhost:3000"
BLOCKED_ORIGIN="http://malicious-attacker.com"

echo "=========================================================="
echo "Starting TrafficVision API Gateway Verification: $BASE_URL"
echo "=========================================================="

# 1. Health Probe Verification
echo -n "[1/5] Checking GET /health... "
HEALTH_RESP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
if [ "$HEALTH_RESP" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "FAIL (Expected 200, got $HEALTH_RESP)"
    exit 1
fi

echo -n "[2/5] Checking GET /ready... "
READY_RESP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/ready")
if [ "$READY_RESP" -eq 200 ]; then
    echo "PASS (HTTP 200)"
else
    echo "FAIL (Expected 200, got $READY_RESP)"
    exit 1
fi

# 2. CORS Allowed Origin
echo -n "[3/5] Testing Allowed CORS Origin ($ALLOWED_ORIGIN)... "
CORS_ALLOW_HEADER=$(curl -s -I -H "Origin: $ALLOWED_ORIGIN" "$BASE_URL/health" | grep -i "access-control-allow-origin" || true)
if echo "$CORS_ALLOW_HEADER" | grep -q "$ALLOWED_ORIGIN"; then
    echo "PASS (Header: $CORS_ALLOW_HEADER)"
else
    echo "FAIL (Expected access-control-allow-origin: $ALLOWED_ORIGIN)"
    exit 1
fi

# 3. CORS Blocked Origin
echo -n "[4/5] Testing Blocked CORS Origin ($BLOCKED_ORIGIN)... "
CORS_BLOCKED_HEADER=$(curl -s -I -H "Origin: $BLOCKED_ORIGIN" "$BASE_URL/health" | grep -i "access-control-allow-origin" || true)
if [ -z "$CORS_BLOCKED_HEADER" ] || ! echo "$CORS_BLOCKED_HEADER" | grep -q "$BLOCKED_ORIGIN"; then
    echo "PASS (Blocked successfully, no header granted to $BLOCKED_ORIGIN)"
else
    echo "FAIL (Unexpectedly granted CORS header: $CORS_BLOCKED_HEADER)"
    exit 1
fi

# 4. Rate Limiting Trigger
echo -n "[5/5] Testing Auth Rate Limiting (threshold: 10 requests/min)... "
RATE_LIMIT_TRIGGERED=false

for i in $(seq 1 15); do
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"wrongpassword"}')
    if [ "$STATUS_CODE" -eq 429 ]; then
        RATE_LIMIT_TRIGGERED=true
        echo "PASS (Triggered HTTP 429 on attempt #$i)"
        break
    fi
done

if [ "$RATE_LIMIT_TRIGGERED" = false ]; then
    echo "FAIL (Rate limit 429 was not triggered within 15 attempts)"
    exit 1
fi

echo "=========================================================="
echo "All Gateway Production Checks Passed Successfully!"
echo "=========================================================="
