import os

import requests
from dotenv import load_dotenv

load_dotenv()


ALERT_CONGESTION_LEVELS = {
    level.strip()
    for level in os.getenv("CONGESTION_ALERT_LEVELS", "High,Severe").split(",")
    if level.strip()
}


ALERT_API_URL = os.getenv("ALERT_API_URL", "")


ALERT_SERVICE_KEY = os.getenv("ALERT_SERVICE_KEY", "")


ALERT_API_TIMEOUT = float(os.getenv("ALERT_API_TIMEOUT", "5"))


ALERT_SEVERITY_MAP = {"Low": "Low", "Medium": "Medium", "High": "High", "Severe": "Critical"}


class CongestionThresholdWatcher:
    """
    Watches live traffic readings and triggers
    an alert when congestion crosses the configured threshold.
    """

    def __init__(self, alert_api_url=None, alert_service_key=None):
        self.alert_api_url = alert_api_url or ALERT_API_URL

        self.alert_service_key = (
            alert_service_key if alert_service_key is not None else ALERT_SERVICE_KEY
        )

        self.active_alert_roads = set()

    def normalize_live_reading(self, reading):
        return {
            "road_id": reading["road_id"],
            "congestion_level": reading["congestion_level"],
            "vehicle_count": reading["vehicle_count"],
            "traffic_density": reading.get("traffic_density", reading.get("density")),
            "avg_speed_kmph": reading.get("avg_speed_kmph"),
            "timestamp": reading.get("timestamp", reading.get("updated_at")),
        }

    def is_threshold_breached(self, reading):
        return reading["congestion_level"] in ALERT_CONGESTION_LEVELS

    def build_alert_payload(self, reading):
        normalized = self.normalize_live_reading(reading)

        congestion_level = normalized["congestion_level"]

        road_id = normalized["road_id"]

        alert_severity = ALERT_SEVERITY_MAP.get(congestion_level, congestion_level)

        message = f"{congestion_level} congestion threshold " f"breached on road {road_id}."

        return {
            "type": "congestion",
            "severity": alert_severity,
            "road_id": road_id,
            "message": message,
        }

    def _build_headers(self):
        headers = {"Content-Type": "application/json"}

        if self.alert_service_key:
            headers["X-Alert-Service-Key"] = self.alert_service_key

        return headers

    def send_alert(self, payload):
        if not self.alert_api_url:
            return {"status": "pending", "message": ("Alert API URL is not configured")}

        headers = self._build_headers()

        try:
            response = requests.post(
                self.alert_api_url, json=payload, headers=headers, timeout=ALERT_API_TIMEOUT
            )

            response.raise_for_status()

            if response.content:
                return response.json()

            return {"status": "created"}

        except requests.RequestException as exc:
            return {"status": "failed", "message": str(exc)}

    def check_reading(self, reading):
        normalized = self.normalize_live_reading(reading)

        road_id = normalized["road_id"]

        congestion_level = normalized["congestion_level"]

        if not self.is_threshold_breached(normalized):
            self.active_alert_roads.discard(road_id)

            return {
                "threshold_breached": False,
                "road_id": road_id,
                "congestion_level": congestion_level,
                "alert_triggered": False,
            }

        if road_id in self.active_alert_roads:
            return {
                "threshold_breached": True,
                "road_id": road_id,
                "congestion_level": congestion_level,
                "alert_triggered": False,
                "reason": "alert_already_active",
            }

        payload = self.build_alert_payload(normalized)

        alert_response = self.send_alert(payload)

        if alert_response.get("status") == "created":
            self.active_alert_roads.add(road_id)

        return {
            "threshold_breached": True,
            "road_id": road_id,
            "congestion_level": congestion_level,
            "alert_triggered": (alert_response.get("status") == "created"),
            "alert_response": alert_response,
        }


def monitor_live_readings(live_readings, alert_api_url=None, alert_service_key=None):
    watcher = CongestionThresholdWatcher(
        alert_api_url=alert_api_url, alert_service_key=alert_service_key
    )

    results = []

    for reading in live_readings:
        result = watcher.check_reading(reading)

        results.append(result)

    return results


if __name__ == "__main__":

    sample_readings = [
        {
            "road_id": "R001",
            "vehicle_count": 82,
            "density": 16.4,
            "congestion_level": "High",
            "updated_at": ("2026-08-31T09:00:00+05:30"),
            "avg_speed_kmph": 22.5,
        }
    ]

    print("\n==========================================")

    print("M3 DAY 2 - CONGESTION THRESHOLD WATCHER")

    print("==========================================")

    print(f"Alert API: {ALERT_API_URL}")

    print("Alert service key configured: " f"{bool(ALERT_SERVICE_KEY)}")

    print(f"Alert levels: " f"{', '.join(ALERT_CONGESTION_LEVELS)}")

    print("\nChecking live traffic reading...")

    results = monitor_live_readings(sample_readings)

    print("\nResult:")

    print(results)
