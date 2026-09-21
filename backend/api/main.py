from datetime import datetime
from pathlib import Path
import sys

AIML_ROOT = Path(__file__).resolve().parents[2] / "aiml"
sys.path.insert(0, str(AIML_ROOT))

import pandas as pd
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.data_engineering_adapter import TrafficDataAdapter
from src.prediction_model import MODEL_VERSION, load_model, predict_observation

app = FastAPI(title="TrafficVision AI Engine")
api_v1_router = APIRouter(prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "external" / "traffic_readings_export.csv"
MODEL_PATH = AIML_ROOT / "models" / "congestion_model.joblib"
MODEL_ARTIFACT = load_model(MODEL_PATH)
TRAFFIC_DATA = TrafficDataAdapter(DATA_PATH)
ROAD_CAPACITY = 200.0
ROAD_NAME_MAP = {
    "R001": "Main Expressway",
    "R002": "Central Avenue",
    "R003": "West Ring Road",
    "R004": "North Boulevard",
    "R005": "Industrial Highway",
    "R006": "Airport Road",
    "R007": "Harbor Tunnel Approach",
}


class CongestionResponse(BaseModel):
    road_id: str
    predicted_level: str
    confidence: float = Field(ge=0, le=1)
    model_version: str
    observed_at: datetime
    density: float = Field(ge=0)


class PeakHoursResponse(BaseModel):
    road_id: str
    peak_windows: list[str]
    model_version: str


class DelayResponse(BaseModel):
    road_id: str
    predicted_level: str
    estimated_delay_minutes: float = Field(ge=0)
    model_version: str


class RouteCandidate(BaseModel):
    route_id: str
    distance_km: float = Field(gt=0)
    roads: list[str] = Field(min_length=1)
    base_duration_minutes: float | None = Field(default=None, ge=0)


class RankedRoute(BaseModel):
    route_id: str
    score: float
    predicted_delay_minutes: float
    predicted_congestion: str


class RouteRankingRequest(BaseModel):
    routes: list[RouteCandidate] = Field(min_length=1)


class TrafficHistoryPoint(BaseModel):
    vehicle_count: int
    density: float
    avg_speed_kmph: float
    congestion_level: str
    updated_at: datetime | str


class TrafficRoad(BaseModel):
    road_id: str
    road_name: str
    vehicle_count: int
    density: float
    avg_speed_kmph: float
    speed: str
    congestion_level: str
    updated_at: datetime | str
    history: list[TrafficHistoryPoint] | None = None


class DensitySummary(BaseModel):
    total_roads: int
    total_roads_monitored: int
    total_vehicle_count: int
    average_density: float
    average_network_density: float
    maximum_density: float
    minimum_density: float
    high_congestion_roads: int = 0
    severe_congestion_roads: int = 0
    congested_segments: int = 0
    timestamp: datetime | str


def _load_traffic_data() -> pd.DataFrame:
    df = TRAFFIC_DATA.load_history()
    return df.sort_values("timestamp").reset_index(drop=True)


def _latest_observation(road_id: str):
    df = _load_traffic_data()
    road_data = df[df["road_id"].astype(str).str.upper() == str(road_id).upper()]
    if road_data.empty:
        return None
    return road_data.sort_values("timestamp").iloc[-1]


def _normalize_congestion_level(value: str | None) -> str:
    if value is None:
        return "Low"
    level = str(value).strip()
    if not level:
        return "Low"
    normalized = level.lower()
    if "severe" in normalized:
        return "Severe"
    if "high" in normalized:
        return "High"
    if "med" in normalized:
        return "Medium"
    return "Low"


def _density_from_vehicle_count(vehicle_count: float | int) -> float:
    return float(vehicle_count) / ROAD_CAPACITY


def _density_from_row(row: pd.Series) -> float:
    value = row.get("density")
    if value is not None and not pd.isna(value):
        return float(value)
    return _density_from_vehicle_count(row["vehicle_count"])


def _road_name(road_id: str) -> str:
    return ROAD_NAME_MAP.get(str(road_id).upper(), f"Road {road_id}")


def _serialize_live_row(row: pd.Series) -> dict:
    vehicle_count = int(row.get("vehicle_count", 0) or 0)
    avg_speed = float(row.get("average_speed", 0) or 0)
    density = _density_from_row(row)
    updated_at = pd.to_datetime(row.get("timestamp")).isoformat()
    return {
        "road_id": str(row["road_id"]),
        "road_name": row.get("road_name") or _road_name(row["road_id"]),
        "vehicle_count": vehicle_count,
        "density": round(density, 3),
        "avg_speed_kmph": round(avg_speed, 2),
        "speed": f"{round(avg_speed)} km/h",
        "congestion_level": _normalize_congestion_level(row.get("congestion_level")),
        "updated_at": updated_at,
    }


def _latest_live_traffic() -> list[dict]:
    df = TRAFFIC_DATA.load_live()
    if df.empty:
        return []
    latest_by_road = df.sort_values("timestamp").groupby("road_id", as_index=False).tail(1)
    return [_serialize_live_row(row) for _, row in latest_by_road.iterrows()]


def _density_summary() -> dict:
    latest_by_road = _load_traffic_data().sort_values("timestamp").groupby("road_id", as_index=False).tail(1)
    if latest_by_road.empty:
        return {
            "total_roads": 0,
            "total_roads_monitored": 0,
            "total_vehicle_count": 0,
            "average_density": 0.0,
            "average_network_density": 0.0,
            "maximum_density": 0.0,
            "minimum_density": 0.0,
            "high_congestion_roads": 0,
            "severe_congestion_roads": 0,
            "congested_segments": 0,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        }

    latest_by_road["density"] = latest_by_road.apply(_density_from_row, axis=1)
    latest_by_road["congestion_level"] = latest_by_road["congestion_level"].apply(_normalize_congestion_level)

    total_roads = int(latest_by_road["road_id"].nunique())
    total_vehicle_count = int(latest_by_road["vehicle_count"].sum())
    densitiy_values = latest_by_road["density"].astype(float)
    high_count = int((latest_by_road["congestion_level"] == "High").sum())
    severe_count = int((latest_by_road["congestion_level"] == "Severe").sum())
    timestamp = latest_by_road["timestamp"].max().isoformat()

    return {
        "total_roads": total_roads,
        "total_roads_monitored": total_roads,
        "total_vehicle_count": total_vehicle_count,
        "average_density": round(float(densitiy_values.mean()), 3),
        "average_network_density": round(float(densitiy_values.mean()), 3),
        "maximum_density": round(float(densitiy_values.max()), 3),
        "minimum_density": round(float(densitiy_values.min()), 3),
        "high_congestion_roads": high_count,
        "severe_congestion_roads": severe_count,
        "congested_segments": high_count + severe_count,
        "timestamp": timestamp,
    }


def _road_history(road_id: str) -> dict:
    df = TRAFFIC_DATA.load_road(road_id) if TRAFFIC_DATA.uses_external_source else _load_traffic_data()
    road_data = df[df["road_id"].astype(str).str.upper() == str(road_id).upper()].sort_values("timestamp")
    if road_data.empty:
        raise HTTPException(status_code=404, detail=f"Road {road_id} not found")

    latest = road_data.iloc[-1]
    history = []
    for _, row in road_data.iterrows():
        history.append({
            "vehicle_count": int(row["vehicle_count"] or 0),
            "density": round(_density_from_row(row), 3),
            "avg_speed_kmph": round(float(row.get("average_speed", 0) or 0), 2),
            "congestion_level": _normalize_congestion_level(row.get("congestion_level")),
            "updated_at": pd.to_datetime(row["timestamp"]).isoformat(),
        })

    payload = {
        "road_id": str(latest["road_id"]),
        "road_name": latest.get("road_name") or _road_name(latest["road_id"]),
        "vehicle_count": int(latest["vehicle_count"] or 0),
        "density": round(_density_from_row(latest), 3),
        "avg_speed_kmph": round(float(latest.get("average_speed", 0) or 0), 2),
        "speed": f"{round(float(latest.get('average_speed', 0) or 0))} km/h",
        "congestion_level": _normalize_congestion_level(latest.get("congestion_level")),
        "updated_at": pd.to_datetime(latest["timestamp"]).isoformat(),
        "history": history,
    }
    return payload


@app.get("/")
def home():
    return {
        "service": "TrafficVision AI Engine",
        "status": "running",
    }


@app.get("/traffic")
def get_traffic():
    df = _load_traffic_data()
    return df.to_dict(orient="records")


@app.get("/congestion")
def get_congestion():
    df = _load_traffic_data()
    result = df[["road_id", "timestamp", "average_speed", "vehicle_count", "congestion_level"]]
    return result.to_dict(orient="records")


@app.get("/traffic/live")
def get_live_traffic():
    return _latest_live_traffic()


@app.get("/traffic/density")
def get_density_summary():
    return _density_summary()


@app.get("/traffic/road/{road_id}")
def get_road_traffic(road_id: str):
    return _road_history(road_id)


@app.get("/predict/congestion", response_model=CongestionResponse)
def predict_congestion_api(
    road_id: str,
    vehicle_count: float | None = Query(default=None, ge=0),
    average_speed: float | None = Query(default=None, ge=0),
    timestamp: datetime | None = None,
) -> CongestionResponse:
    """Predict from a live observation, or the latest local record as a fallback."""
    latest = _latest_observation(road_id)

    if vehicle_count is None or average_speed is None or timestamp is None:
        if latest is None:
            raise HTTPException(status_code=404, detail=f"Road {road_id} not found")
        vehicle_count = float(latest["vehicle_count"])
        average_speed = float(latest["average_speed"])
        timestamp = pd.to_datetime(latest["timestamp"]).to_pydatetime()

    density = _density_from_vehicle_count(vehicle_count)
    if latest is not None and vehicle_count == float(latest["vehicle_count"]):
        density = _density_from_row(latest)
    prediction = predict_observation(
        MODEL_ARTIFACT,
        road_id,
        vehicle_count,
        average_speed,
        pd.Timestamp(timestamp),
        density=density,
    )

    return CongestionResponse(
        road_id=road_id,
        predicted_level=prediction["predicted_level"],
        confidence=prediction["confidence"],
        model_version=prediction["model_version"],
        observed_at=timestamp,
        density=density,
    )


@app.get("/predict/peak-hours", response_model=PeakHoursResponse)
def predict_peak_hours(road_id: str) -> PeakHoursResponse:
    if _latest_observation(road_id) is None:
        raise HTTPException(status_code=404, detail=f"Road {road_id} not found")
    return PeakHoursResponse(
        road_id=road_id,
        peak_windows=["08:00-10:59", "17:00-19:59"],
        model_version=MODEL_VERSION,
    )


@app.get("/predict/delay", response_model=DelayResponse)
def predict_delay(
    road_id: str,
    distance_km: float = Query(default=1.0, gt=0),
    vehicle_count: float | None = Query(default=None, ge=0),
    average_speed: float | None = Query(default=None, ge=0),
    timestamp: datetime | None = None,
) -> DelayResponse:
    congestion = predict_congestion_api(road_id, vehicle_count, average_speed, timestamp)
    speed_factor = {"LOW": 1.0, "MEDIUM": 1.35, "HIGH": 1.8, "SEVERE": 2.2}.get(congestion.predicted_level.upper(), 1.0)
    free_flow_minutes = distance_km / 50.0 * 60.0
    return DelayResponse(
        road_id=road_id,
        predicted_level=congestion.predicted_level,
        estimated_delay_minutes=round(free_flow_minutes * (speed_factor - 1), 2),
        model_version=congestion.model_version,
    )


@app.post("/route/rank", response_model=list[RankedRoute])
def rank_routes(request: RouteRankingRequest) -> list[RankedRoute]:
    ranked = []
    for route in request.routes:
        predictions = [predict_congestion_api(road_id) for road_id in route.roads]
        delay = sum(
            {"LOW": 0.0, "MEDIUM": 0.35, "HIGH": 0.8, "SEVERE": 1.2}[prediction.predicted_level]
            * route.distance_km for prediction in predictions
        )
        congestion_score = sum(
            {"LOW": 0.0, "MEDIUM": 1.0, "HIGH": 2.0, "SEVERE": 3.0}[prediction.predicted_level]
            for prediction in predictions
        )
        ranked.append(RankedRoute(
            route_id=route.route_id,
            score=round((route.base_duration_minutes or route.distance_km) + delay, 3),
            predicted_delay_minutes=round(delay, 3),
            predicted_congestion=("SEVERE" if congestion_score >= 3 else "HIGH" if congestion_score >= 2 else "MEDIUM" if congestion_score else "LOW"),
        ))
    return sorted(ranked, key=lambda route: route.score)


@api_v1_router.get("/traffic/live")
def get_live_traffic_v1():
    return get_live_traffic()


@api_v1_router.get("/traffic/density")
def get_density_summary_v1():
    return get_density_summary()


@api_v1_router.get("/traffic/road/{road_id}")
def get_road_traffic_v1(road_id: str):
    return get_road_traffic(road_id)


@api_v1_router.get("/predict/congestion", response_model=CongestionResponse)
def predict_congestion_api_v1(
    road_id: str,
    vehicle_count: float | None = Query(default=None, ge=0),
    average_speed: float | None = Query(default=None, ge=0),
    timestamp: datetime | None = None,
) -> CongestionResponse:
    return predict_congestion_api(road_id, vehicle_count, average_speed, timestamp)


@api_v1_router.get("/predict/peak-hours", response_model=PeakHoursResponse)
def predict_peak_hours_v1(road_id: str) -> PeakHoursResponse:
    return predict_peak_hours(road_id)


@api_v1_router.get("/predict/delay", response_model=DelayResponse)
def predict_delay_v1(
    road_id: str,
    distance_km: float = Query(default=1.0, gt=0),
    vehicle_count: float | None = Query(default=None, ge=0),
    average_speed: float | None = Query(default=None, ge=0),
    timestamp: datetime | None = None,
) -> DelayResponse:
    return predict_delay(road_id, distance_km, vehicle_count, average_speed, timestamp)


@api_v1_router.post("/route/rank", response_model=list[RankedRoute])
def rank_routes_v1(request: RouteRankingRequest) -> list[RankedRoute]:
    return rank_routes(request)


app.include_router(api_v1_router)