#!/usr/bin/env bash
# ==============================================================================
# TrafficVision AI — Workflow Validation Runner
# ==============================================================================

set -e

BASE_URL="${1:-http://127.0.0.1:8080}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 &>/dev/null; then
    python3 "$SCRIPT_DIR/validate-workflows.py" "$BASE_URL"
elif command -v python &>/dev/null; then
    python "$SCRIPT_DIR/validate-workflows.py" "$BASE_URL"
else
    echo "Python is required to execute workflow validations."
    exit 1
fi
