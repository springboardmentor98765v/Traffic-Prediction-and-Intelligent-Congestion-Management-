"""Milestone 4 Day 3 — deploy stage driver for Render (used by .github/workflows/ci.yml).

Deploys one commit to every Render service and waits until each is live:

    python QA/milestone4/day3/render_deploy.py deploy --commit <sha> --state deploy_state.json
    python QA/milestone4/day3/render_deploy.py rollback --state deploy_state.json

Environment:
    RENDER_API_KEY      Render account API key (Account Settings -> API Keys)
    RENDER_SERVICE_IDS  name=srv-id pairs, comma-separated, e.g.
                        backend=srv-aaa,analytics=srv-bbb,ai=srv-ccc,web=srv-ddd

`deploy` records which deploy was live before (the rollback target) in --state. If any
service fails to build or start, the services that already went live are rolled back and
the script exits non-zero. `rollback` is used by CI when the post-deploy health gate fails.
Stdlib only, so it runs on a bare GitHub runner.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.render.com/v1"
LIVE = "live"
FAILED = {"build_failed", "update_failed", "canceled", "deactivated", "pre_deploy_failed"}


def api(method, path, body=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={
            "Authorization": f"Bearer {os.environ['RENDER_API_KEY']}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise SystemExit(f"Render API {method} {path} -> {exc.code}: {detail}") from exc
    return json.loads(raw) if raw else None


def unwrap(item):
    # List endpoints wrap each object as {"deploy": {...}, "cursor": "..."}.
    return item.get("deploy", item) if isinstance(item, dict) else item


def parse_services():
    raw = os.environ.get("RENDER_SERVICE_IDS", "")
    services = {}
    for pair in filter(None, (p.strip() for p in raw.split(","))):
        name, _, service_id = pair.partition("=")
        if not service_id:
            raise SystemExit(f"Bad RENDER_SERVICE_IDS entry {pair!r}; expected name=srv-id")
        services[name.strip()] = service_id.strip()
    if not services:
        raise SystemExit("RENDER_SERVICE_IDS is empty")
    return services


def current_live_deploy(service_id):
    for item in api("GET", f"/services/{service_id}/deploys?limit=20") or []:
        deploy = unwrap(item)
        if deploy.get("status") == LIVE:
            return deploy["id"]
    return None


def rollback(state):
    ok = True
    for name, entry in state.items():
        previous = entry.get("previous")
        if not entry.get("went_live"):
            continue
        if not previous:
            print(f"  {name}: no earlier live deploy to roll back to")
            ok = False
            continue
        api("POST", f"/services/{entry['service_id']}/rollback", {"deployId": previous})
        print(f"  {name}: rolling back to {previous}")
    return ok


def deploy(commit, state_path, timeout):
    services = parse_services()
    state = {}
    for name, service_id in services.items():
        previous = current_live_deploy(service_id)
        new = unwrap(api("POST", f"/services/{service_id}/deploys", {"commitId": commit}))
        state[name] = {
            "service_id": service_id,
            "previous": previous,
            "deploy": new["id"],
            "status": new.get("status"),
            "went_live": False,
        }
        print(f"{name:10} deploy {new['id']} started (previous live: {previous})")

    deadline = time.monotonic() + timeout
    pending = set(state)
    while pending and time.monotonic() < deadline:
        time.sleep(15)
        for name in sorted(pending):
            entry = state[name]
            status = unwrap(
                api("GET", f"/services/{entry['service_id']}/deploys/{entry['deploy']}")
            )["status"]
            if status != entry["status"]:
                print(f"{name:10} {status}")
                entry["status"] = status
            if status == LIVE:
                entry["went_live"] = True
                pending.discard(name)
            elif status in FAILED:
                pending.discard(name)

    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)

    failed = [n for n, e in state.items() if not e["went_live"]]
    if not failed:
        print(f"\nAll {len(state)} services live on {commit[:12]}")
        return 0

    for name in failed:
        status = state[name]["status"]
        print(f"FAIL {name}: {status if status in FAILED else 'timed out (' + str(status) + ')'}")
    print("Rolling back the services that went live, so all services stay on one release:")
    rollback(state)
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["deploy", "rollback"])
    parser.add_argument("--commit", help="git SHA to deploy (deploy only)")
    parser.add_argument("--state", default="deploy_state.json")
    # Free-tier Docker builds are slow (shared CPU); 25 minutes covers a cold build of all three.
    parser.add_argument("--timeout", type=int, default=1500, help="seconds to wait for live")
    args = parser.parse_args()

    if not os.environ.get("RENDER_API_KEY"):
        raise SystemExit("RENDER_API_KEY is not set")

    if args.action == "deploy":
        if not args.commit:
            raise SystemExit("--commit is required for deploy")
        return deploy(args.commit, args.state, args.timeout)

    with open(args.state, encoding="utf-8") as fh:
        state = json.load(fh)
    print("Rolling back to the previous release:")
    return 0 if rollback(state) else 1


if __name__ == "__main__":
    sys.exit(main())
