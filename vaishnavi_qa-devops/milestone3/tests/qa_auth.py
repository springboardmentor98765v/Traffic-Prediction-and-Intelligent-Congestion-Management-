"""Shared auth helpers for the Milestone 3 QA scripts.

Alerts need credentials since the DEF-M3-005 fix:
- users/operators/admins read alerts with their own JWT (``role_token``);
- producers (congestion watcher, anomaly detector) post with the internal
  ``X-Alert-Service-Key`` header (``service_headers``), value from ALERT_SERVICE_KEY.

Rebuilt 2026-09-26 from its compiled copy after the source file went missing.
"""

import json
import os
import subprocess
import urllib.error
import urllib.request
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PG = "trafficvision-postgres-dev"
PASSWORD = "QaPass#2026"


def load_dev_env(path=REPO_ROOT / ".env.dev"):
    """Set ALERT_SERVICE_KEY (and friends) from .env.dev unless already in the environment."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.lstrip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() in ("ALERT_SERVICE_KEY",):
            os.environ.setdefault(key.strip(), value.strip())


def service_headers():
    load_dev_env()
    key = os.environ.get("ALERT_SERVICE_KEY", "")
    return {"X-Alert-Service-Key": key} if key else {}


def _post(url, body):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        return exc.code, None


def role_token(base_url, role, tag="qa"):
    """Register a fresh account, promote it to `role` (user/operator/admin), return its JWT."""
    run = uuid.uuid4().hex[:8]
    email = f"{tag}.{role}.{run}@gmail.com"
    status, _ = _post(
        f"{base_url}/api/v1/auth/register",
        {"name": f"{tag.replace('.', '_')}_{role}_{run}", "email": email, "password": PASSWORD},
    )
    assert status == 201, f"register {role}: {status}"
    if role != "user":
        subprocess.run(
            [
                "docker",
                "exec",
                PG,
                "psql",
                "-U",
                "traffic",
                "-d",
                "trafficvision",
                "-tAc",
                f"UPDATE users SET role='{role}' WHERE email='{email}'",
            ],
            capture_output=True,
            check=True,
        )
    status, body = _post(f"{base_url}/api/v1/auth/login", {"email": email, "password": PASSWORD})
    assert status == 200, f"login {role}: {status}"
    return body["access_token"]
