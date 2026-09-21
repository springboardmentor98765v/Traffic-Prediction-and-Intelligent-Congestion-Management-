from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


EXTERNAL_FIELD_MAP = {
    "recorded_at": "timestamp",
    "updated_at": "timestamp",
    "avg_speed_kmph": "average_speed",
}


class TrafficDataAdapter:
    """Adapt the Data Engineering traffic API to the AI/ML dataframe schema."""

    def __init__(self, local_path: str | Path, api_url: str | None = None, timeout: float = 5.0):
        self.local_path = Path(local_path)
        self.api_url = (api_url or os.getenv("TRAFFIC_DATA_API_URL", "")).rstrip("/")
        self.timeout = timeout

    @property
    def uses_external_source(self) -> bool:
        return bool(self.api_url)

    def _get_json(self, path: str, params: dict | None = None):
        url = f"{self.api_url}/{path.lstrip('/')}"
        if params:
            url = f"{url}?{urlencode(params)}"
        with urlopen(url, timeout=self.timeout) as response:
            return json.load(response)

    @staticmethod
    def _rows(payload) -> list[dict]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("readings", "data", "results", "items"):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        raise ValueError("Traffic API response does not contain a list of readings")

    @staticmethod
    def _canonicalize(rows: list[dict]) -> pd.DataFrame:
        if not rows:
            return pd.DataFrame(columns=["road_id", "timestamp", "vehicle_count", "average_speed", "congestion_level"])

        frame = pd.DataFrame(rows).rename(columns=EXTERNAL_FIELD_MAP)
        required = {"road_id", "timestamp", "vehicle_count", "average_speed"}
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"Traffic API response is missing fields: {sorted(missing)}")

        frame["road_id"] = frame["road_id"].astype(str)
        frame["timestamp"] = pd.to_datetime(frame["timestamp"])
        frame["vehicle_count"] = pd.to_numeric(frame["vehicle_count"], errors="raise")
        frame["average_speed"] = pd.to_numeric(frame["average_speed"], errors="raise")
        if "congestion_level" not in frame.columns:
            frame["congestion_level"] = "LOW"
        frame["congestion_level"] = (
            frame["congestion_level"].astype(str).str.upper().replace({"MODERATE": "MEDIUM"})
        )
        return frame.sort_values(["road_id", "timestamp"]).reset_index(drop=True)

    def load_history(self) -> pd.DataFrame:
        if not self.uses_external_source:
            return self._canonicalize(pd.read_csv(self.local_path).to_dict(orient="records"))
        payload = self._get_json("traffic/history", {"limit": 10000})
        return self._canonicalize(self._rows(payload))

    def load_live(self) -> pd.DataFrame:
        if not self.uses_external_source:
            return self.load_history()
        payload = self._get_json("traffic/live")
        return self._canonicalize(self._rows(payload))

    def load_road(self, road_id: str) -> pd.DataFrame:
        if not self.uses_external_source:
            frame = self.load_history()
            return frame[frame["road_id"].str.upper() == road_id.upper()]

        payload = self._get_json(f"traffic/road/{road_id}")
        rows = payload.get("history", []) if isinstance(payload, dict) else []
        current = payload if isinstance(payload, dict) else {}
        if current:
            rows = [*rows, {
                "road_id": current.get("road_id", road_id),
                "recorded_at": current.get("updated_at"),
                "vehicle_count": current.get("vehicle_count"),
                "avg_speed_kmph": current.get("avg_speed_kmph"),
                "density": current.get("density"),
                "congestion_level": current.get("congestion_level"),
            }]
        return self._canonicalize(rows)

    def source_name(self) -> str:
        return "data-engineering-api" if self.uses_external_source else "local-processed-csv"
