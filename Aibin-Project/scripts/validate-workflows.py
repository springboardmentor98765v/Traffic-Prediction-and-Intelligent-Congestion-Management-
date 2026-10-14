#!/usr/bin/env python3
"""
TrafficVision AI — End-to-End Workflow Validation Tool
Milestone 4: Testing, Deployment & Documentation

Executes the complete live workflow chain across all backend systems via the API Gateway:
Step 1: Auth & RBAC (Register, Login, Role Enforcement)
Step 2: Monitoring (Live traffic & Road status)
Step 3: Prediction (Congestion classification, delay, peak hours)
Step 4: Route Analysis (Route optimization, alternate routes, corridor conditions)
Step 5: Alerts (Create alert, list active alerts, acknowledge/mark read)
Step 6: Analytics & AI Insights (Trends, heatmaps, AI recommendations)

Usage:
    python scripts/validate-workflows.py [BASE_URL]
"""

import sys
import time
import requests
from typing import Dict, Any, Optional

class WorkflowValidator:
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.results = []
        self.admin_token = None
        self.commuter_token = None
        self.created_alert_id = None

    def record(self, step_num: int, name: str, endpoint: str, method: str, expected_code: int, resp: Optional[requests.Response], duration_ms: float, error_msg: Optional[str] = None):
        actual_code = resp.status_code if resp is not None else 0
        passed = (actual_code == expected_code) if resp is not None else False
        status_str = "PASS" if passed else "FAIL"

        result_entry = {
            "step": step_num,
            "name": name,
            "method": method,
            "endpoint": endpoint,
            "expected_code": expected_code,
            "actual_code": actual_code,
            "duration_ms": duration_ms,
            "status": status_str,
            "error": error_msg or ("" if passed else (resp.text[:120] if resp is not None else "Connection error"))
        }
        self.results.append(result_entry)

        symbol = "[PASS]" if passed else "[FAIL]"
        timing = f"{duration_ms:.1f}ms"
        print(f"[{step_num:02d}] {status_str:<4} | {method:<4} {endpoint:<45} | HTTP {actual_code} (exp {expected_code}) | {timing:>7} | {name}")
        if not passed and result_entry["error"]:
            print(f"     +-- Error: {result_entry['error']}")

        return passed

    def _execute(self, step_num: int, name: str, method: str, path: str, expected_code: int, token: Optional[str] = None, json_body: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[requests.Response]:
        url = f"{self.base_url}{path}"
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        start = time.time()
        resp = None
        error_msg = None
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_body,
                params=params,
                timeout=35
            )
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"

        duration_ms = (time.time() - start) * 1000
        self.record(step_num, name, path, method, expected_code, resp, duration_ms, error_msg)
        return resp

    def run_all(self) -> bool:
        print("=" * 100)
        print(f"TrafficVision AI — End-to-End Workflow Validation Suite")
        print(f"Target Gateway: {self.base_url}")
        print("=" * 100)

        step = 1

        # ----------------------------------------------------------------------
        # PHASE 1: System Health & Probes
        # ----------------------------------------------------------------------
        print("\n--- PHASE 1: Gateway System Probes ---")
        self._execute(step, "Gateway Liveness Probe", "GET", "/health", 200)
        step += 1

        self._execute(step, "Database Readiness Probe", "GET", "/ready", 200)
        step += 1

        # ----------------------------------------------------------------------
        # PHASE 2: Auth & RBAC Verification
        # ----------------------------------------------------------------------
        print("\n--- PHASE 2: Authentication & RBAC ---")
        # Register new commuter
        unique_email = f"commuter_{int(time.time())}@trafficvision.ai"
        reg_resp = self._execute(
            step, "Register New Commuter", "POST", "/api/v1/auth/register", 201,
            json_body={"name": "Live Tester", "email": unique_email, "password": "CommuterPassword@123", "role": "commuter"}
        )
        step += 1

        # Login as Admin
        admin_login = self._execute(
            step, "Admin Authentication Login", "POST", "/api/v1/auth/login", 200,
            json_body={"email": "admin@trafficvision.ai", "password": "Admin@12345"}
        )
        if admin_login and admin_login.status_code == 200:
            self.admin_token = admin_login.json().get("access_token")
        step += 1

        # Login as Commuter
        commuter_login = self._execute(
            step, "Commuter Authentication Login", "POST", "/api/v1/auth/login", 200,
            json_body={"email": "commuter@trafficvision.ai", "password": "Commuter@123"}
        )
        if commuter_login and commuter_login.status_code == 200:
            self.commuter_token = commuter_login.json().get("access_token")
        step += 1

        # Verify Current User Profile
        self._execute(step, "Verify User Profile (/me)", "GET", "/api/v1/auth/me", 200, token=self.admin_token)
        step += 1

        # RBAC Check: Commuter forbidden from accessing Admin-only road detail
        self._execute(step, "RBAC Security: Commuter Blocked from Road Admin", "GET", "/api/v1/traffic/road/1", 403, token=self.commuter_token)
        step += 1

        # ----------------------------------------------------------------------
        # PHASE 3: Monitoring & Density
        # ----------------------------------------------------------------------
        print("\n--- PHASE 3: Traffic Monitoring ---")
        self._execute(step, "Get Live Traffic Stream", "GET", "/api/v1/traffic/live", 200, token=self.admin_token)
        step += 1

        self._execute(step, "Get Overall Traffic Density", "GET", "/api/v1/traffic/density", 200, token=self.admin_token)
        step += 1

        self._execute(step, "Get Specific Road Status", "GET", "/api/v1/traffic/road/1", 200, token=self.admin_token)
        step += 1

        # ----------------------------------------------------------------------
        # PHASE 4: AI/ML Prediction Engine
        # ----------------------------------------------------------------------
        print("\n--- PHASE 4: AI Predictions ---")
        self._execute(
            step, "ML Congestion Classification", "GET", "/api/v1/predict/congestion", 200,
            token=self.admin_token, params={"road_id": "1", "density": 0.75, "vehicle_count": 80}
        )
        step += 1

        self._execute(
            step, "ML Travel Delay Estimation", "GET", "/api/v1/predict/delay", 200,
            token=self.admin_token, params={"road_id": "1", "density": 0.75, "vehicle_count": 80}
        )
        step += 1

        self._execute(
            step, "Peak Rush-Hour Status", "GET", "/api/v1/predict/peak-hours", 200,
            token=self.admin_token, params={"hour": 18}
        )
        step += 1

        # ----------------------------------------------------------------------
        # PHASE 5: Route Analysis & Recommendations
        # ----------------------------------------------------------------------
        print("\n--- PHASE 5: Route Analysis ---")
        self._execute(
            step, "Corridor Path Optimization (OSRM)", "GET", "/api/v1/route/optimize", 200,
            token=self.admin_token, params={"origin": "12.9716,77.5946", "destination": "12.9352,77.6245"}
        )
        step += 1

        self._execute(
            step, "Alternative Candidate Routes", "GET", "/api/v1/route/alternate", 200,
            token=self.admin_token, params={"origin": "12.9716,77.5946", "destination": "12.9352,77.6245", "max_routes": 2}
        )
        step += 1

        self._execute(
            step, "Live Road Corridor Conditions", "GET", "/api/v1/route/conditions", 200,
            token=self.admin_token, params={"road_id": "1"}
        )
        step += 1

        # ----------------------------------------------------------------------
        # PHASE 6: Alerts & Incident Management
        # ----------------------------------------------------------------------
        print("\n--- PHASE 6: Alerts & Incident Management ---")
        create_alert_resp = self._execute(
            step, "Create Congestion Incident Alert", "POST", "/api/v1/alerts", 200,
            token=self.admin_token,
            json_body={"type": "congestion", "severity": "medium", "road_id": "1", "message": "Heavy traffic detected on Main Corridor"}
        )
        if create_alert_resp and create_alert_resp.status_code == 200:
            data = create_alert_resp.json()
            self.created_alert_id = data.get("alert_id") or data.get("id") or 1
        else:
            self.created_alert_id = 1
        step += 1

        self._execute(step, "List Active System Alerts", "GET", "/api/v1/alerts/active", 200, token=self.admin_token)
        step += 1

        self._execute(
            step, f"Acknowledge / Mark Alert #{self.created_alert_id} Read", "POST", f"/api/v1/alerts/{self.created_alert_id}/read", 200,
            token=self.admin_token
        )
        step += 1

        # ----------------------------------------------------------------------
        # PHASE 7: Analytics & AI Insights
        # ----------------------------------------------------------------------
        print("\n--- PHASE 7: Analytics & AI Insights ---")
        self._execute(
            step, "Traffic Trends Analytics", "GET", "/api/v1/analytics/trends", 200,
            token=self.admin_token, params={"road_id": 1, "range": "week"}
        )
        step += 1

        self._execute(
            step, "Incident Heatmap Analytics", "GET", "/api/v1/analytics/heatmap", 200,
            token=self.admin_token, params={"range": "week"}
        )
        step += 1

        self._execute(
            step, "AI Intelligent Recommendations", "GET", "/api/v1/predict/recommendations", 200,
            token=self.admin_token, params={"road_id": "1", "density": 0.8, "vehicle_count": 90}
        )
        step += 1

        # Summary computation
        total_steps = len(self.results)
        passed_steps = sum(1 for r in self.results if r["status"] == "PASS")
        failed_steps = total_steps - passed_steps

        print("\n" + "=" * 100)
        print(f"VALIDATION SUMMARY: {passed_steps}/{total_steps} Passed ({failed_steps} Failed)")
        print("=" * 100)

        return failed_steps == 0

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
    validator = WorkflowValidator(target)
    success = validator.run_all()
    sys.exit(0 if success else 1)
