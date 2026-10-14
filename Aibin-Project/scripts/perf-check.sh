#!/usr/bin/env bash
# TrafficVision AI - Performance Benchmarking Shell Wrapper (Milestone 4)
set -e

BASE_URL=${1:-"http://127.0.0.1:8080"}
ROUNDS=${2:-25}

echo "Running performance benchmarks against ${BASE_URL} (Rounds: ${ROUNDS})..."

if command -v python3 &>/dev/null; then
    python3 "$(dirname "$0")/perf_check.py" "${BASE_URL}" "${ROUNDS}"
elif command -v python &>/dev/null; then
    python "$(dirname "$0")/perf_check.py" "${BASE_URL}" "${ROUNDS}"
else
    echo "Python runtime is required to run performance benchmarks."
    exit 1
fi
