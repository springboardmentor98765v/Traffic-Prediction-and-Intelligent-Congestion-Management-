from datetime import datetime
import base64
import csv
import hashlib
import hmac
import io
import math
import json
import os
from pathlib import Path
import secrets
import sys
import time
from html import escape

AIML_ROOT = Path(__file__).resolve().parents[2] / "aiml"
sys.path.insert(0, str(AIML_ROOT))

from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import httpx
import sklearn
from fastapi import APIRouter, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.data_engineering_adapter import TrafficDataAdapter
from src.model_evaluation import evaluate_saved_model
from src.prediction_model import MODEL_VERSION, build_features, load_model, normalize_road_id, predict_observation
from api.state_store import open_state

app = FastAPI(title="TrafficVision AI Engine")
api_v1_router = APIRouter(prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Disposition"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "external" / "traffic_readings_export.csv"
MODEL_PATH = AIML_ROOT / "models" / "source_ml_v2.joblib"
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
AUTH_DATA_PATH = PROJECT_ROOT / "data" / "users.json"
DEFAULT_ADMIN_EMAIL = "admin.gmail.com"
DEFAULT_ADMIN_NAME = "System Administrator"
DEFAULT_ADMIN_PASSWORD = os.getenv("TRAFFICVISION_DEFAULT_ADMIN_PASSWORD")
AUTH_SECRET = os.getenv("TRAFFICVISION_AUTH_SECRET") or secrets.token_urlsafe(32)
CAPTCHA_TTL_SECONDS = 300
CAPTCHA_CHALLENGES: Dict[str, Tuple[str, float]] = {}


class AuthCredentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class CaptchaVerification(BaseModel):
    challenge_id: str = Field(min_length=1)
    captcha_response: str = Field(min_length=1, max_length=12)


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    name: str


class CaptchaResponse(BaseModel):
    challenge_id: str
    image: str


class RegisterRequest(AuthCredentials, CaptchaVerification):
    name: str = Field(min_length=1, max_length=100)
    role: Optional[str] = None


class LoginRequest(AuthCredentials, CaptchaVerification):
    pass


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class UserProfile(BaseModel):
    email: str
    name: str
    role: str


def _read_users() -> Dict[str, dict]:
    if not AUTH_DATA_PATH.exists():
        return {}
    try:
        return json.loads(AUTH_DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _ensure_default_admin() -> Dict[str, dict]:
    users = _read_users()
    if DEFAULT_ADMIN_EMAIL not in users and DEFAULT_ADMIN_PASSWORD:
        users[DEFAULT_ADMIN_EMAIL] = {
            "name": DEFAULT_ADMIN_NAME,
            "role": "ADMIN",
            "password_hash": _hash_password(DEFAULT_ADMIN_PASSWORD),
        }
        _write_users(users)
    return users


def _write_users(users: Dict[str, dict]) -> None:
    AUTH_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTH_DATA_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        salt_text, digest_text = encoded.split("$", 1)
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _encode_token(email: str, role: str, expires_in: int, token_type: str, jti: str) -> str:
    payload = {
        "sub": email,
        "role": role,
        "exp": int(time.time()) + expires_in,
        "type": token_type,
        "jti": jti,
    }
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(AUTH_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    return f"{body}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"


def _issue_auth_response(email: str, user: dict) -> AuthResponse:
    role = str(user["role"]).upper()
    expires_at = int(time.time()) + 7 * 24 * 3600
    refresh_jti = secrets.token_urlsafe(24)
    access_token = _encode_token(email, role, 3600, "access", secrets.token_urlsafe(18))
    refresh_token = _encode_token(email, role, 7 * 24 * 3600, "refresh", refresh_jti)
    with open_state() as connection:
        connection.execute(
            "INSERT INTO auth_sessions (refresh_jti, email, role, expires_at) VALUES (?, ?, ?, ?)",
            (refresh_jti, email, role, expires_at),
        )
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=role,
        name=user["name"],
    )


def _decode_token(token: str) -> dict:
    try:
        body, signature = token.split(".", 1)
        expected = hmac.new(AUTH_SECRET.encode(), body.encode(), hashlib.sha256).digest()
        actual = base64.urlsafe_b64decode(signature + "=")
        if not hmac.compare_digest(actual, expected):
            raise ValueError("Invalid token")
        payload = json.loads(base64.urlsafe_b64decode(body + "===").decode())
        if int(payload["exp"]) < int(time.time()):
            raise ValueError("Expired token")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, base64.binascii.Error) as error:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from error


def _create_captcha_svg(code: str) -> str:
    safe_code = escape(code)
    return ("<svg xmlns='http://www.w3.org/2000/svg' width='140' height='42' viewBox='0 0 140 42'>"
            "<rect width='140' height='42' fill='#0d1527'/><path d='M0 30 C35 2 95 40 140 10' "
            "stroke='#5679a5' stroke-width='2' fill='none'/><path d='M0 8 C40 35 100 0 140 32' "
            "stroke='#315274' stroke-width='2' fill='none'/><text x='10' y='29' fill='#8dcdff' "
            "font-family='monospace' font-size='22' font-weight='bold' letter-spacing='5'>" + safe_code + "</text></svg>")


def _consume_captcha(challenge_id: str, response: str) -> None:
    challenge = CAPTCHA_CHALLENGES.pop(challenge_id, None)
    if not challenge or challenge[1] < time.time() or not hmac.compare_digest(challenge[0], response.strip().upper()):
        raise HTTPException(status_code=400, detail="Invalid or expired CAPTCHA")


def _authenticated_user(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = _decode_token(authorization.split(" ", 1)[1].strip())
    if payload.get("type") not in (None, "access"):
        raise HTTPException(status_code=401, detail="An access token is required")
    user = _read_users().get(payload["sub"])
    if not user or user.get("role") != payload.get("role"):
        raise HTTPException(status_code=401, detail="Invalid user session")
    return {**user, "email": payload["sub"]}


def _require_alert_manager(authorization: Optional[str]) -> dict:
    user = _authenticated_user(authorization)
    if str(user.get("role", "")).upper() not in {"ADMIN", "OPERATOR", "TRAFFIC_OPERATOR"}:
        raise HTTPException(status_code=403, detail="Only traffic operators can manage alerts")
    return user


@api_v1_router.get("/auth/captcha", response_model=CaptchaResponse)
def create_captcha() -> CaptchaResponse:
    challenge_id = secrets.token_urlsafe(18)
    code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(5))
    CAPTCHA_CHALLENGES[challenge_id] = (code, time.time() + CAPTCHA_TTL_SECONDS)
    image = "data:image/svg+xml;base64," + base64.b64encode(_create_captcha_svg(code).encode()).decode()
    return CaptchaResponse(challenge_id=challenge_id, image=image)


@api_v1_router.post("/auth/register", response_model=UserProfile, status_code=201)
def register_user(request: RegisterRequest) -> UserProfile:
    _consume_captcha(request.challenge_id, request.captcha_response)
    email = request.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email address is required")
    users = _read_users()
    if email in users:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    users[email] = {
        "name": request.name.strip(),
        "role": "USER",
        "password_hash": _hash_password(request.password),
    }
    _write_users(users)
    return UserProfile(email=email, name=users[email]["name"], role="USER")


@api_v1_router.post("/auth/login", response_model=AuthResponse)
def login_user(request: LoginRequest) -> AuthResponse:
    _consume_captcha(request.challenge_id, request.captcha_response)
    email = request.email.strip().lower()
    users = _ensure_default_admin()
    user = users.get(email)
    if not user or not _verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _issue_auth_response(email, user)


@api_v1_router.post("/auth/refresh", response_model=AuthResponse)
def refresh_user(request: RefreshRequest) -> AuthResponse:
    payload = _decode_token(request.refresh_token)
    refresh_jti = payload.get("jti")
    if payload.get("type") != "refresh" or not refresh_jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    with open_state() as connection:
        session = connection.execute(
            "SELECT email, role, expires_at, revoked_at FROM auth_sessions WHERE refresh_jti = ?",
            (refresh_jti,),
        ).fetchone()
        if (
            session is None
            or session["revoked_at"] is not None
            or int(session["expires_at"]) <= int(time.time())
            or session["email"] != payload.get("sub")
            or session["role"] != payload.get("role")
        ):
            raise HTTPException(status_code=401, detail="Invalid or expired refresh session")
        connection.execute(
            "UPDATE auth_sessions SET revoked_at = ? WHERE refresh_jti = ?",
            (int(time.time()), refresh_jti),
        )
    user = _read_users().get(payload["sub"])
    if not user or user.get("role") != payload.get("role"):
        raise HTTPException(status_code=401, detail="Invalid user session")
    return _issue_auth_response(payload["sub"], user)


@api_v1_router.post("/auth/logout")
def logout_user(request: LogoutRequest) -> dict:
    payload = _decode_token(request.refresh_token)
    refresh_jti = payload.get("jti")
    if payload.get("type") != "refresh" or not refresh_jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    with open_state() as connection:
        cursor = connection.execute(
            "UPDATE auth_sessions SET revoked_at = ? WHERE refresh_jti = ? AND revoked_at IS NULL",
            (int(time.time()), refresh_jti),
        )
        if cursor.rowcount != 1:
            raise HTTPException(status_code=401, detail="Refresh session is already revoked or unknown")
    return {"status": "logged_out"}


@api_v1_router.get("/auth/me", response_model=UserProfile)
def current_user(authorization: Optional[str] = Header(default=None)) -> UserProfile:
    user = _authenticated_user(authorization)
    return UserProfile(email=user["email"], name=user["name"], role=user["role"])


class CongestionResponse(BaseModel):
    road_id: str
    predicted_level: str
    confidence: float = Field(ge=0, le=1)
    model_version: str
    observed_at: datetime
    vehicle_count: int = Field(ge=0)
    average_speed: float = Field(ge=0)
    density: float = Field(ge=0)
    factors: Dict[str, float]


class PeakHoursResponse(BaseModel):
    road_id: str
    peak_windows: List[str]
    hourly_data: List[dict]
    observed_through: Any
    data_source: str
    model_version: str


class DelayResponse(BaseModel):
    road_id: str
    predicted_level: str
    estimated_delay_minutes: float = Field(ge=0)
    model_version: str


class ModelAccuracyResponse(BaseModel):
    model_version: str
    accuracy: float = Field(ge=0, le=1)
    macro_precision: float = Field(ge=0, le=1)
    macro_recall: float = Field(ge=0, le=1)
    macro_f1: float = Field(ge=0, le=1)
    weighted_f1: float = Field(ge=0, le=1)
    evaluation_valid: bool
    evaluation_note: str


class ModelMetricsResponse(BaseModel):
    model_version: str
    accuracy: float = Field(ge=0, le=1)
    macro_precision: float = Field(ge=0, le=1)
    macro_recall: float = Field(ge=0, le=1)
    macro_f1: float = Field(ge=0, le=1)
    weighted_f1: float = Field(ge=0, le=1)
    evaluation_valid: bool
    evaluation_note: str
    training_rows: int = Field(ge=0)
    test_rows: int = Field(ge=0)
    rows: int = Field(ge=0)
    classes: List[str]
    per_class: Dict[str, Any]
    confusion_matrix: List[List[int]]
    confusion_matrix_labels: List[str]
    feature_importance: List[Dict[str, Any]]
    test_start: datetime
    test_end: datetime
    evaluation_method: str
    leakage_checks: Dict[str, bool]
    artifact_metric_cross_check: Dict[str, Any]
    label_caveat: str


class RouteCandidate(BaseModel):
    route_id: str
    distance_km: float = Field(gt=0)
    roads: List[str] = Field(min_length=1)
    base_duration_minutes: Optional[float] = Field(default=None, ge=0)


class RankedRoute(BaseModel):
    route_id: str
    score: float
    predicted_delay_minutes: float
    predicted_congestion: str
    distance_km: float = 0.0
    estimated_travel_time_minutes: float = 0.0
    rank: int = 0
    is_recommended: bool = False
    available: bool = True
    road_predictions: List[dict] = Field(default_factory=list)


class RouteRankingRequest(BaseModel):
    routes: List[RouteCandidate] = Field(min_length=1)


class TrafficHistoryPoint(BaseModel):
    vehicle_count: int
    density: float
    avg_speed_kmph: float
    congestion_level: str
    updated_at: Any


class TrafficRoad(BaseModel):
    road_id: str
    road_name: str
    vehicle_count: int
    density: float
    avg_speed_kmph: float
    speed: str
    congestion_level: str
    updated_at: Any
    history: Optional[List[TrafficHistoryPoint]] = None


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
    timestamp: Any


def _load_traffic_data() -> pd.DataFrame:
    try:
        df = TRAFFIC_DATA.load_history()
    except Exception as error:
        raise HTTPException(status_code=503, detail="Traffic data source is unavailable") from error
    if df.empty:
        raise HTTPException(status_code=503, detail="Traffic data source returned no records")
    return df.sort_values("timestamp").reset_index(drop=True)


def _latest_observation(road_id: str):
    df = _load_traffic_data()
    road_key = normalize_road_id(road_id)
    road_data = df[df["road_id"].astype(str).str.upper() == road_key]
    if road_data.empty:
        return None
    return road_data.sort_values("timestamp").iloc[-1]


def _normalize_congestion_level(value: Optional[str]) -> str:
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


def _density_from_vehicle_count(vehicle_count: Union[float, int]) -> float:
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
        "length_km": float(row.get("length_km")) if row.get("length_km") is not None and not pd.isna(row.get("length_km")) else None,
        "vehicle_count": vehicle_count,
        "density": round(density, 3),
        "avg_speed_kmph": round(avg_speed, 2),
        "speed": f"{round(avg_speed)} km/h",
        "congestion_level": _normalize_congestion_level(row.get("congestion_level")),
        "updated_at": updated_at,
    }


def _latest_live_traffic() -> List[dict]:
    try:
        df = TRAFFIC_DATA.load_live()
    except Exception as error:
        raise HTTPException(status_code=503, detail="Traffic data source is unavailable") from error
    if df.empty:
        raise HTTPException(status_code=503, detail="Traffic data source returned no records")
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
    road_id = normalize_road_id(road_id)
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


@app.get("/health")
def health():
    traffic = _load_traffic_data()
    return {
        "status": "healthy",
        "service": app.title,
        "traffic_source": TRAFFIC_DATA.source_name(),
        "traffic_records": int(len(traffic)),
        "roads": sorted(traffic["road_id"].astype(str).unique().tolist()),
        "model_version": MODEL_ARTIFACT.get("model_version", MODEL_VERSION),
    }


@app.get("/health/detailed")
def detailed_health():
    traffic = _load_traffic_data()
    with open_state() as connection:
        connection.execute("SELECT 1")
    return {
        "status": "healthy",
        "service": app.title,
        "dependencies": {
            "traffic_data": {"status": "healthy", "source": TRAFFIC_DATA.source_name(), "records": int(len(traffic))},
            "model": {"status": "healthy", "version": MODEL_ARTIFACT.get("model_version", MODEL_VERSION), "scikit_learn": sklearn.__version__},
            "state_store": {"status": "healthy", "kind": "sqlite-local-state"},
        },
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
    vehicle_count: Optional[float] = Query(default=None, ge=0),
    average_speed: Optional[float] = Query(default=None, ge=0),
    timestamp: Optional[datetime] = None,
) -> CongestionResponse:
    """Predict from a live observation, or the latest local record as a fallback."""
    road_id = normalize_road_id(road_id)
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
        vehicle_count=int(vehicle_count),
        average_speed=float(average_speed),
        density=density,
        factors={
            "vehicle_count": float(vehicle_count),
            "average_speed": float(average_speed),
            "density": float(density),
        },
    )


@app.get("/predict/peak-hours", response_model=PeakHoursResponse)
def predict_peak_hours(road_id: str) -> PeakHoursResponse:
    road_id = normalize_road_id(road_id)
    frame = _load_traffic_data()
    road_rows = frame[frame["road_id"].astype(str).str.upper() == road_id]
    if road_rows.empty:
        raise HTTPException(status_code=404, detail=f"Road {road_id} not found")
    road_rows = road_rows.copy()
    road_rows["hour"] = pd.to_datetime(road_rows["timestamp"]).dt.hour
    hourly_data = []
    for hour, group in road_rows.groupby("hour"):
        hourly_data.append({
            "hour": int(hour),
            "avg_vehicle_count": round(float(group["vehicle_count"].mean()), 1),
            "avg_speed_kmph": round(float(group["average_speed"].mean()), 2),
            "avg_density": round(float(group.apply(_density_from_row, axis=1).mean()), 3),
            "sample_count": int(len(group)),
        })
    busiest_hours = sorted(hourly_data, key=lambda item: item["avg_vehicle_count"], reverse=True)[:3]
    peak_windows = [f"{item['hour']:02d}:00-{item['hour']:02d}:59" for item in busiest_hours]
    return PeakHoursResponse(
        road_id=road_id,
        peak_windows=peak_windows,
        hourly_data=sorted(hourly_data, key=lambda item: item["hour"]),
        observed_through=pd.to_datetime(road_rows["timestamp"].max()).isoformat(),
        data_source=TRAFFIC_DATA.source_name(),
        model_version=MODEL_VERSION,
    )


@app.get("/predict/delay", response_model=DelayResponse)
def predict_delay(
    road_id: str,
    distance_km: float = Query(default=1.0, gt=0),
    vehicle_count: Optional[float] = Query(default=None, ge=0),
    average_speed: Optional[float] = Query(default=None, ge=0),
    timestamp: Optional[datetime] = None,
) -> DelayResponse:
    road_id = normalize_road_id(road_id)
    congestion = predict_congestion_api(road_id, vehicle_count, average_speed, timestamp)
    speed_factor = {"LOW": 1.0, "MEDIUM": 1.35, "HIGH": 1.8, "SEVERE": 2.2}.get(congestion.predicted_level.upper(), 1.0)
    free_flow_minutes = distance_km / 50.0 * 60.0
    return DelayResponse(
        road_id=road_id,
        predicted_level=congestion.predicted_level,
        estimated_delay_minutes=round(free_flow_minutes * (speed_factor - 1), 2),
        model_version=congestion.model_version,
    )


@app.post("/route/rank", response_model=List[RankedRoute])
def rank_routes(request: RouteRankingRequest) -> List[RankedRoute]:
    ranked = []
    for route in request.routes:
        road_ids = [normalize_road_id(road_id) for road_id in route.roads]
        history = _load_traffic_data()
        road_lengths = []
        for road_id in road_ids:
            road_rows = history[history["road_id"].astype(str) == road_id]
            length = float(road_rows.iloc[-1].get("length_km", 0) or 0) if not road_rows.empty else 0.0
            road_lengths.append(length if math.isfinite(length) and length > 0 else 0.0)
        total_length = sum(road_lengths)
        segment_distances = (
            [route.distance_km * length / total_length for length in road_lengths]
            if total_length > 0 else [route.distance_km / len(road_ids)] * len(road_ids)
        )
        road_predictions = []
        for road_id, segment_distance in zip(road_ids, segment_distances):
            prediction = predict_congestion_api(road_id)
            level = prediction.predicted_level.upper()
            multiplier = {"LOW": 1.0, "MEDIUM": 1.35, "HIGH": 1.8, "SEVERE": 2.2}[level]
            base_minutes = (route.base_duration_minutes * segment_distance / route.distance_km
                            if route.base_duration_minutes is not None else segment_distance / 50.0 * 60.0)
            travel_minutes = base_minutes * multiplier
            road_predictions.append({
                "road_id": road_id,
                "predicted_congestion": level,
                "confidence": prediction.confidence,
                "distance_km": round(segment_distance, 3),
                "predicted_delay_minutes": round(travel_minutes - base_minutes, 2),
                "estimated_travel_time_minutes": round(travel_minutes, 2),
            })
        delay = sum(item["predicted_delay_minutes"] for item in road_predictions)
        travel_time = sum(item["estimated_travel_time_minutes"] for item in road_predictions)
        worst_level = max(
            (item["predicted_congestion"] for item in road_predictions),
            key=lambda level: {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "SEVERE": 3}[level],
        )
        ranked.append(RankedRoute(
            route_id=route.route_id,
            score=round(100.0 / (1.0 + travel_time), 4),
            predicted_delay_minutes=round(delay, 2),
            predicted_congestion=worst_level,
            distance_km=route.distance_km,
            estimated_travel_time_minutes=round(travel_time, 2),
            road_predictions=road_predictions,
        ))
    ranked.sort(key=lambda route: (-route.score, route.distance_km))
    for index, route in enumerate(ranked, 1):
        route.rank = index
        route.is_recommended = index == 1
    return ranked


def _get_model_metrics() -> dict:
    metrics = MODEL_ARTIFACT.get("metrics") if isinstance(MODEL_ARTIFACT, dict) else None
    if not metrics:
        raise HTTPException(status_code=404, detail="Model evaluation metrics not found in artifact")
    return metrics


@app.get("/model/accuracy", response_model=ModelAccuracyResponse, tags=["Model Evaluation"])
def get_model_accuracy() -> ModelAccuracyResponse:
    metrics = evaluate_saved_model(MODEL_PATH, DATA_PATH)
    return ModelAccuracyResponse(
        model_version=metrics["model_version"],
        accuracy=metrics["accuracy"],
        macro_precision=metrics["macro_precision"],
        macro_recall=metrics["macro_recall"],
        macro_f1=metrics["macro_f1"],
        weighted_f1=metrics["weighted_f1"],
        evaluation_valid=metrics["evaluation_valid"],
        evaluation_note=metrics["evaluation_note"],
    )


@app.get("/model/metrics", response_model=ModelMetricsResponse, tags=["Model Evaluation"])
def get_model_metrics() -> ModelMetricsResponse:
    metrics = evaluate_saved_model(MODEL_PATH, DATA_PATH)
    return ModelMetricsResponse(
        **metrics,
    )


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
    vehicle_count: Optional[float] = Query(default=None, ge=0),
    average_speed: Optional[float] = Query(default=None, ge=0),
    timestamp: Optional[datetime] = None,
) -> CongestionResponse:
    return predict_congestion_api(road_id, vehicle_count, average_speed, timestamp)


@api_v1_router.get("/predict/peak-hours", response_model=PeakHoursResponse)
def predict_peak_hours_v1(road_id: str) -> PeakHoursResponse:
    return predict_peak_hours(road_id)


@api_v1_router.get("/predict/delay", response_model=DelayResponse)
def predict_delay_v1(
    road_id: str,
    distance_km: float = Query(default=1.0, gt=0),
    vehicle_count: Optional[float] = Query(default=None, ge=0),
    average_speed: Optional[float] = Query(default=None, ge=0),
    timestamp: Optional[datetime] = None,
) -> DelayResponse:
    return predict_delay(road_id, distance_km, vehicle_count, average_speed, timestamp)


@api_v1_router.post("/route/rank", response_model=List[RankedRoute])
def rank_routes_v1(request: RouteRankingRequest) -> List[RankedRoute]:
    return rank_routes(request)


OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org").rstrip("/")


def _parse_coordinate(value: str) -> Tuple[float, float]:
    try:
        latitude, longitude = (float(part.strip()) for part in value.split(","))
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=422, detail="Coordinates must use lat,lng format") from error
    if not math.isfinite(latitude) or not math.isfinite(longitude) or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="Coordinates are outside valid latitude/longitude bounds")
    return latitude, longitude


async def _fetch_osrm_routes(origin: Tuple[float, float], destination: Tuple[float, float], alternatives: bool) -> dict:
    coordinates = f"{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coordinates}"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, params={
                "overview": "full",
                "geometries": "geojson",
                "alternatives": str(alternatives).lower(),
            })
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(status_code=503, detail="OSRM routing service is unavailable") from error
    if payload.get("code") != "Ok" or not payload.get("routes"):
        raise HTTPException(status_code=404, detail="OSRM found no drivable route between these coordinates")
    return payload


def _cache_osrm_route(route: dict) -> dict:
    geometry = route.get("geometry") if isinstance(route, dict) else None
    coordinates = geometry.get("coordinates", []) if isinstance(geometry, dict) else []
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        raise HTTPException(status_code=502, detail="OSRM route did not include usable geometry")
    try:
        path = [[float(latitude), float(longitude)] for longitude, latitude in coordinates]
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=502, detail="OSRM route geometry was malformed") from error
    route_id = "route-" + hashlib.sha256(
        ";".join(f"{latitude:.6f},{longitude:.6f}" for latitude, longitude in path).encode("utf-8")
    ).hexdigest()[:12]
    payload = {
        "route_id": route_id,
        "path": path,
        "distance_km": round(float(route["distance"]) / 1000.0, 2),
        "base_duration_minutes": round(float(route["duration"]) / 60.0, 2),
        "source": "OSRM",
        "traffic_impact_available": False,
        "traffic_impact_note": "No road-ID-to-geometry map matching is configured; route traffic impact is not inferred.",
    }
    with open_state() as connection:
        connection.execute(
            "INSERT INTO route_cache (route_id, payload_json, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT(route_id) DO UPDATE SET payload_json = excluded.payload_json, created_at = excluded.created_at",
            (route_id, json.dumps(payload), datetime.utcnow().isoformat(timespec="seconds") + "+00:00"),
        )
    return payload


@api_v1_router.get("/route/optimize")
async def optimize_route(origin: str, destination: str):
    parsed_origin = _parse_coordinate(origin)
    parsed_destination = _parse_coordinate(destination)
    try:
        payload = await _fetch_osrm_routes(parsed_origin, parsed_destination, alternatives=False)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="OSRM routing service is unavailable") from error
    return _cache_osrm_route(payload["routes"][0])


@api_v1_router.get("/route/alternate")
async def alternate_routes(origin: str, destination: str):
    parsed_origin = _parse_coordinate(origin)
    parsed_destination = _parse_coordinate(destination)
    try:
        payload = await _fetch_osrm_routes(parsed_origin, parsed_destination, alternatives=True)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="OSRM routing service is unavailable") from error
    routes = [_cache_osrm_route(route) for route in payload["routes"]]
    routes.sort(key=lambda route: (route["base_duration_minutes"], route["distance_km"]))
    return [{**route, "rank": index, "is_recommended": index == 1} for index, route in enumerate(routes, 1)]


@api_v1_router.get("/route/travel-time")
def get_route_travel_time(route_id: str):
    with open_state() as connection:
        route = connection.execute("SELECT payload_json FROM route_cache WHERE route_id = ?", (route_id,)).fetchone()
    if route is None:
        raise HTTPException(status_code=404, detail="Unknown route_id. Call /route/optimize or /route/alternate first")
    payload = json.loads(route["payload_json"])
    return {
        "route_id": route_id,
        "estimated_minutes": payload["base_duration_minutes"],
        "based_on": "OSRM road-network estimate; no live traffic map matching",
        "traffic_impact_available": False,
    }


@api_v1_router.get("/model/accuracy", response_model=ModelAccuracyResponse, tags=["Model Evaluation"])
def get_model_accuracy_v1():
    return get_model_accuracy()


@api_v1_router.get("/model/metrics", response_model=ModelMetricsResponse, tags=["Model Evaluation"])
def get_model_metrics_v1():
    return get_model_metrics()


@api_v1_router.get("/predict/model-info", tags=["Model Evaluation"])
def get_model_info():
    metrics = evaluate_saved_model(MODEL_PATH, DATA_PATH)
    classifier = MODEL_ARTIFACT["model"].named_steps["classifier"]
    return {
        "model_name": "TrafficVision Congestion Predictor",
        "model_version": MODEL_ARTIFACT.get("model_version", MODEL_VERSION),
        "model_type": type(classifier).__name__,
        "framework": "scikit-learn",
        "scikit_learn_version": sklearn.__version__,
        "data_source": TRAFFIC_DATA.source_name(),
        "dataset_records": metrics["rows"],
        "features": ["road_id", "vehicle_count", "average_speed", "density", "hour", "day_of_week", "is_peak_hour", "recent_congestion"],
        "classes": metrics["classes"],
        "evaluation": {
            "accuracy": metrics["accuracy"],
            "macro_precision": metrics["macro_precision"],
            "macro_recall": metrics["macro_recall"],
            "macro_f1": metrics["macro_f1"],
            "weighted_f1": metrics["weighted_f1"],
            "training_rows": metrics["training_rows"],
            "test_rows": metrics["test_rows"],
            "test_start": metrics["test_start"],
            "test_end": metrics["test_end"],
        },
        "label_caveat": metrics["label_caveat"],
    }


@api_v1_router.get("/predict/model-metrics", tags=["Model Evaluation"])
def get_model_metrics_alias():
    return evaluate_saved_model(MODEL_PATH, DATA_PATH)



# ---------------------------------------------------------------------------
# Frontend integration contracts: alerts, analytics, heatmap, reports,
# recommendations.
#
# These endpoints derive their responses from the same real traffic data
# adapter/model already used above. They do not invent coordinates or claim
# to be an external routing provider.
# ---------------------------------------------------------------------------

class AlertResponse(BaseModel):
    alert_id: str
    road_id: str
    road_name: str
    level: str
    title: str
    message: str
    vehicle_count: Optional[int] = None
    density: Optional[float] = None
    avg_speed_kmph: Optional[float] = None
    created_at: Any
    status: str = "ACTIVE"
    type: str = "congestion"
    severity: str = "medium"
    read: bool = False


class CreateAlertRequest(BaseModel):
    type: str = Field(min_length=1, max_length=32)
    severity: str = Field(min_length=1, max_length=32)
    road_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=3, max_length=1000)


class AnalyticsResponse(BaseModel):
    period: str
    total_roads: int
    total_vehicle_count: int
    average_density: float
    average_speed_kmph: float
    congestion_counts: Dict[str, int]
    roads: List[dict]


class HeatmapPoint(BaseModel):
    road_id: str
    road_name: str
    density: float
    congestion_level: str
    vehicle_count: int
    avg_speed_kmph: float
    timestamp: Any


class HistoricalReportResponse(BaseModel):
    road_id: str
    road_name: str
    from_timestamp: Any
    to_timestamp: Any
    total_records: int
    average_vehicle_count: float
    average_density: float
    average_speed_kmph: float
    congestion_counts: Dict[str, int]
    history: List[dict]


class RecommendationResponse(BaseModel):
    road_id: str
    road_name: str
    congestion_level: str
    priority: str
    recommendation: str
    reason: str
    model_version: str


class TrafficAnomaly(BaseModel):
    road_id: str
    timestamp: Any
    observed_congestion: str
    predicted_congestion: str
    severity: str
    reason: str
    confidence: float = Field(ge=0, le=1)
    anomaly_score: float = Field(ge=0, le=1)


class AnomalyResponse(BaseModel):
    anomalies: List[TrafficAnomaly]
    evaluated_rows: int = Field(ge=0)
    model_version: str
    data_source: str
    interpretation: str


def _build_alerts() -> List[dict]:
    rows = _latest_live_traffic()
    alerts = []
    for row in rows:
        level = _normalize_congestion_level(row.get("congestion_level"))
        if level not in {"High", "Severe"}:
            continue

        alert_id = "ALERT-" + hashlib.sha1(
            f"{row['road_id']}:{row['updated_at']}:{level}".encode("utf-8")
        ).hexdigest()[:10].upper()

        priority = "CRITICAL" if level == "Severe" else "HIGH"
        alerts.append({
            "alert_id": alert_id,
            "road_id": row["road_id"],
            "road_name": row["road_name"],
            "type": "congestion",
            "severity": "critical" if level == "Severe" else "high",
            "level": level,
            "title": f"{level} congestion detected",
            "message": (
                f"{row['road_name']} is currently reporting {level.lower()} "
                f"congestion with {row['vehicle_count']} vehicles."
            ),
            "vehicle_count": row["vehicle_count"],
            "density": row["density"],
            "avg_speed_kmph": row["avg_speed_kmph"],
            "created_at": row["updated_at"],
            "status": "ACTIVE",
            "priority": priority,
        })
    with open_state() as connection:
        read_ids = {
            item["alert_id"]
            for item in connection.execute("SELECT alert_id FROM alert_reads").fetchall()
        }
    for alert in alerts:
        alert["read"] = alert["alert_id"] in read_ids
    return alerts


def _all_alerts() -> List[dict]:
    alerts = _build_alerts()
    existing_ids = {alert["alert_id"] for alert in alerts}
    with open_state() as connection:
        stored = connection.execute(
            "SELECT * FROM alerts ORDER BY created_at DESC"
        ).fetchall()
    for item in stored:
        if item["alert_id"] in existing_ids:
            continue
        latest = _latest_observation(item["road_id"])
        alerts.append({
            "alert_id": item["alert_id"],
            "road_id": item["road_id"],
            "road_name": (latest.get("road_name") if latest is not None else None) or _road_name(item["road_id"]),
            "type": item["type"],
            "severity": item["severity"],
            "level": item["severity"].title(),
            "title": item["title"],
            "message": item["message"],
            "vehicle_count": item["vehicle_count"],
            "density": item["density"],
            "avg_speed_kmph": item["avg_speed_kmph"],
            "created_at": item["created_at"],
            "status": item["status"],
            "read": bool(item["is_read"]),
        })
    return sorted(alerts, key=lambda item: item["created_at"], reverse=True)


def _build_analytics() -> dict:
    rows = _latest_live_traffic()
    if not rows:
        return {
            "period": "latest",
            "total_roads": 0,
            "total_vehicle_count": 0,
            "average_density": 0.0,
            "average_speed_kmph": 0.0,
            "congestion_counts": {},
            "roads": [],
        }

    counts: Dict[str, int] = {}
    for row in rows:
        level = row["congestion_level"]
        counts[level] = counts.get(level, 0) + 1

    return {
        "period": "latest",
        "total_roads": len(rows),
        "total_vehicle_count": sum(r["vehicle_count"] for r in rows),
        "average_density": round(
            sum(r["density"] for r in rows) / len(rows), 3
        ),
        "average_speed_kmph": round(
            sum(r["avg_speed_kmph"] for r in rows) / len(rows), 2
        ),
        "congestion_counts": counts,
        "roads": rows,
    }


def _build_heatmap() -> List[dict]:
    return [
        {
            "road_id": row["road_id"],
            "road_name": row["road_name"],
            "density": row["density"],
            "congestion_level": row["congestion_level"],
            "vehicle_count": row["vehicle_count"],
            "avg_speed_kmph": row["avg_speed_kmph"],
            "timestamp": row["updated_at"],
        }
        for row in _latest_live_traffic()
    ]


def _build_report(road_id: str) -> dict:
    road_id = normalize_road_id(road_id)
    df = TRAFFIC_DATA.load_road(road_id) if TRAFFIC_DATA.uses_external_source else _load_traffic_data()
    road_data = df[
        df["road_id"].astype(str).str.upper() == str(road_id).upper()
    ].sort_values("timestamp")

    if road_data.empty:
        raise HTTPException(status_code=404, detail=f"Road {road_id} not found")

    densities = road_data.apply(_density_from_row, axis=1)
    levels = road_data["congestion_level"].apply(_normalize_congestion_level)
    counts = levels.value_counts().to_dict()

    history = []
    for _, row in road_data.iterrows():
        history.append({
            "vehicle_count": int(row.get("vehicle_count", 0) or 0),
            "density": round(_density_from_row(row), 3),
            "avg_speed_kmph": round(float(row.get("average_speed", 0) or 0), 2),
            "congestion_level": _normalize_congestion_level(
                row.get("congestion_level")
            ),
            "updated_at": pd.to_datetime(row["timestamp"]).isoformat(),
        })

    return {
        "road_id": str(road_id),
        "road_name": road_data.iloc[-1].get("road_name") or _road_name(road_id),
        "from_timestamp": pd.to_datetime(road_data["timestamp"].min()).isoformat(),
        "to_timestamp": pd.to_datetime(road_data["timestamp"].max()).isoformat(),
        "total_records": int(len(road_data)),
        "average_vehicle_count": round(float(road_data["vehicle_count"].mean()), 2),
        "average_density": round(float(densities.mean()), 3),
        "average_speed_kmph": round(float(road_data["average_speed"].mean()), 2),
        "congestion_counts": {str(k): int(v) for k, v in counts.items()},
        "history": history,
    }


def _build_recommendations() -> List[dict]:
    recommendations = []
    for row in _latest_live_traffic():
        level = row["congestion_level"]
        if level == "Severe":
            recommendation = "Prioritize alternate routing and traffic intervention."
            priority = "CRITICAL"
        elif level == "High":
            recommendation = "Consider alternate routes and active traffic monitoring."
            priority = "HIGH"
        elif level == "Medium":
            recommendation = "Monitor traffic conditions and prepare for possible delay."
            priority = "MEDIUM"
        else:
            recommendation = "No immediate traffic intervention required."
            priority = "LOW"

        recommendations.append({
            "road_id": row["road_id"],
            "road_name": row["road_name"],
            "congestion_level": level,
            "priority": priority,
            "recommendation": recommendation,
            "reason": (
                f"Current density is {row['density']:.3f}, "
                f"average speed is {row['avg_speed_kmph']:.2f} km/h, "
                f"and vehicle count is {row['vehicle_count']}."
            ),
            "model_version": MODEL_VERSION,
        })
    return recommendations


def _build_anomalies(limit: int, window_rows: int) -> dict:
    history = _load_traffic_data()
    if "congestion_level" not in history or history["congestion_level"].isna().all():
        return {
            "anomalies": [],
            "evaluated_rows": 0,
            "model_version": MODEL_ARTIFACT.get("model_version", MODEL_VERSION),
            "data_source": TRAFFIC_DATA.source_name(),
            "interpretation": "Observed congestion labels are unavailable; no comparisons were made.",
        }

    history_features = build_features(history)
    scored = history.tail(window_rows).copy()
    features = history_features.loc[scored.index]
    metrics = MODEL_ARTIFACT.get("metrics", {})
    evaluation_model = MODEL_ARTIFACT.get("evaluation_model")
    if evaluation_model is not None and metrics.get("test_start") and metrics.get("test_end"):
        timestamps = pd.to_datetime(scored["timestamp"])
        evaluation_mask = timestamps.between(
            pd.Timestamp(metrics["test_start"]), pd.Timestamp(metrics["test_end"])
        )
    else:
        evaluation_mask = pd.Series(False, index=scored.index)
    predictions = pd.Series(index=scored.index, dtype="string")
    confidences = pd.Series(index=scored.index, dtype=float)
    for mask, model in ((evaluation_mask, evaluation_model), (~evaluation_mask, MODEL_ARTIFACT["model"])):
        if model is None or not mask.any():
            continue
        model_features = features.loc[mask]
        predictions.loc[mask] = model.predict(model_features)
        confidences.loc[mask] = model.predict_proba(model_features).max(axis=1)
    level_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "SEVERE": 3}
    anomalies = []
    evaluated_rows = 0

    for (index, row) in scored.iterrows():
        if pd.isna(row["congestion_level"]):
            continue
        observed = str(row["congestion_level"]).upper().replace("MODERATE", "MEDIUM")
        predicted = str(predictions.loc[index]).upper()
        if observed not in level_order or predicted not in level_order:
            continue
        evaluated_rows += 1
        distance = abs(level_order[observed] - level_order[predicted])
        if distance:
            anomalies.append({
                "road_id": str(row["road_id"]),
                "timestamp": pd.to_datetime(row["timestamp"]).isoformat(),
                "observed_congestion": observed,
                "predicted_congestion": predicted,
                "severity": "high" if distance >= 2 else "moderate",
                "reason": f"Observed and modelled congestion differ by {distance} level(s).",
                "confidence": float(confidences.loc[index]),
                "anomaly_score": round(distance / 3.0, 3),
            })

    anomalies.sort(key=lambda item: (item["timestamp"], item["severity"] == "high"), reverse=True)
    return {
        "anomalies": anomalies[:limit],
        "evaluated_rows": evaluated_rows,
        "model_version": MODEL_ARTIFACT.get("model_version", MODEL_VERSION),
        "data_source": TRAFFIC_DATA.source_name(),
        "interpretation": (
            "These are prediction/observation mismatches and potential incident proxies only; "
            "they do not establish that an accident occurred."
        ),
    }


@api_v1_router.get("/alerts", response_model=List[AlertResponse])
def get_alerts():
    return _all_alerts()


@api_v1_router.post("/alerts", status_code=201)
def create_alert(request: CreateAlertRequest, authorization: Optional[str] = Header(default=None)):
    _require_alert_manager(authorization)
    alert_type = request.type.strip().lower()
    severity = request.severity.strip().lower()
    if alert_type not in {"congestion", "accident", "closure", "delay", "hazard"}:
        raise HTTPException(status_code=422, detail="Unsupported alert type")
    if severity not in {"low", "medium", "high", "critical"}:
        raise HTTPException(status_code=422, detail="Unsupported alert severity")
    road_id = normalize_road_id(request.road_id)
    latest = _latest_observation(road_id)
    if latest is None:
        raise HTTPException(status_code=404, detail=f"Road {road_id} not found")

    alert_id = "ALERT-" + secrets.token_hex(12).upper()
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "+00:00"
    with open_state() as connection:
        connection.execute(
            "INSERT INTO alerts (alert_id, road_id, type, severity, title, message, vehicle_count, density, avg_speed_kmph, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                alert_id, road_id, alert_type, severity,
                f"{severity.title()} {alert_type} alert", request.message.strip(),
                int(latest["vehicle_count"]), _density_from_row(latest),
                float(latest["average_speed"]), created_at,
            ),
        )
    return {"alert_id": alert_id, "road_id": road_id, "status": "created", "created_at": created_at}


@api_v1_router.get("/alerts/my", response_model=List[AlertResponse])
def get_my_alerts(authorization: Optional[str] = Header(default=None), limit: int = Query(default=50, ge=1, le=200)):
    user = _authenticated_user(authorization)
    alerts = _all_alerts()
    if str(user.get("role", "USER")).upper() in {"USER", "PUBLIC"}:
        alerts = [
            alert for alert in alerts
            if alert["severity"] in {"high", "critical"}
            or alert["type"] in {"accident", "closure", "hazard"}
        ]
    return alerts[:limit]


@api_v1_router.get("/alerts/active", response_model=List[AlertResponse])
def get_active_alerts(road_id: Optional[str] = None, limit: int = Query(default=50, ge=1, le=200)):
    normalized_road = normalize_road_id(road_id) if road_id else None
    alerts = [item for item in _all_alerts() if item["status"] == "ACTIVE" and not item["read"]]
    if normalized_road:
        alerts = [item for item in alerts if item["road_id"] == normalized_road]
    return alerts[:limit]


@api_v1_router.post("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: str):
    if not any(item["alert_id"] == alert_id for item in _all_alerts()):
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")
    read_at = datetime.utcnow().isoformat(timespec="seconds") + "+00:00"
    with open_state() as connection:
        stored = connection.execute("UPDATE alerts SET is_read = 1 WHERE alert_id = ?", (alert_id,))
        if stored.rowcount == 0:
            connection.execute(
                "INSERT INTO alert_reads (alert_id, read_at) VALUES (?, ?) "
                "ON CONFLICT(alert_id) DO UPDATE SET read_at = excluded.read_at",
                (alert_id, read_at),
            )
    return {"alert_id": alert_id, "read": True}


@api_v1_router.post("/alerts/sync-ai-anomalies")
def sync_ai_anomalies(
    minimum_score: float = Query(default=0.3, ge=0, le=1),
    authorization: Optional[str] = Header(default=None),
):
    _require_alert_manager(authorization)
    result = _build_anomalies(limit=100, window_rows=2000)
    created = 0
    skipped = 0
    with open_state() as connection:
        for anomaly in result["anomalies"]:
            if anomaly["anomaly_score"] < minimum_score:
                skipped += 1
                continue
            source_key = "|".join((anomaly["road_id"], anomaly["timestamp"], anomaly["observed_congestion"], anomaly["predicted_congestion"]))
            alert_id = "AI-" + hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:24].upper()
            cursor = connection.execute(
                "INSERT OR IGNORE INTO alerts (alert_id, source_key, road_id, type, severity, title, message, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    alert_id, source_key, anomaly["road_id"], "congestion",
                    "high" if anomaly["severity"] == "high" else "medium",
                    "Traffic model mismatch",
                    f"Observed {anomaly['observed_congestion']}; model predicted {anomaly['predicted_congestion']}. {anomaly['reason']} This is not a confirmed incident.",
                    anomaly["timestamp"],
                ),
            )
            created += cursor.rowcount
            skipped += 1 - cursor.rowcount
    return {"source": result["data_source"], "anomalies_received": len(result["anomalies"]), "alerts_created": created, "alerts_skipped": skipped}


@api_v1_router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    return _build_analytics()


@api_v1_router.get("/heatmap", response_model=List[HeatmapPoint])
def get_heatmap():
    return _build_heatmap()


@api_v1_router.get(
    "/reports/historical/{road_id}",
    response_model=HistoricalReportResponse,
)
def get_historical_report(road_id: str):
    return _build_report(road_id)


@api_v1_router.get(
    "/historical/{road_id}",
    response_model=HistoricalReportResponse,
)
def get_historical_report_alias(road_id: str):
    return _build_report(road_id)


@api_v1_router.get(
    "/recommendations",
    response_model=List[RecommendationResponse],
)
def get_recommendations():
    return _build_recommendations()


@api_v1_router.get(
    "/ai/recommendations",
    response_model=List[RecommendationResponse],
)
def get_ai_recommendations_alias():
    return _build_recommendations()


@api_v1_router.get("/ai/anomalies", response_model=AnomalyResponse)
def get_ai_anomalies(
    limit: int = Query(default=20, ge=1, le=100),
    window_rows: int = Query(default=2000, ge=1, le=10000),
):
    return _build_anomalies(limit, window_rows)


def _history_in_range(frame: pd.DataFrame, range_name: str) -> pd.DataFrame:
    if frame.empty:
        return frame
    latest = pd.Timestamp(frame["timestamp"].max())
    if range_name == "day":
        start = latest.normalize()
    elif range_name == "week":
        start = latest - pd.Timedelta(days=7)
    else:
        start = latest - pd.Timedelta(days=30)
    return frame[frame["timestamp"].between(start, latest)].copy()


def _congestion_score(level: Any) -> float:
    return {"LOW": 0.15, "MEDIUM": 0.45, "HIGH": 0.75, "SEVERE": 0.95}.get(
        str(level).upper(), 0.0
    )


def _road_condition_data(road_id: str) -> dict:
    road_id = normalize_road_id(road_id)
    latest = _latest_observation(road_id)
    if latest is None:
        raise HTTPException(status_code=404, detail=f"Road {road_id} not found")
    with open_state() as connection:
        condition = connection.execute(
            "SELECT status, notes, updated_at FROM road_conditions WHERE road_id = ?",
            (road_id,),
        ).fetchone()
    return {
        "road_id": road_id,
        "road_name": latest.get("road_name") or _road_name(road_id),
        "status": condition["status"] if condition else _normalize_congestion_level(latest.get("congestion_level")),
        "notes": condition["notes"] if condition else "Observed congestion from the imported CSV; no closure, construction, or hazard feed is configured.",
        "vehicle_count": int(latest["vehicle_count"]),
        "average_speed": float(latest["average_speed"]),
        "density": _density_from_row(latest),
        "updated_at": condition["updated_at"] if condition else pd.to_datetime(latest["timestamp"]).isoformat(),
        "condition_source": "stored-road-condition" if condition else "traffic-csv-congestion-only",
    }


@api_v1_router.get("/traffic/history")
def get_traffic_history(
    road_id: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(default=100, ge=1, le=50000),
):
    frame = _load_traffic_data()
    if road_id:
        road_key = normalize_road_id(road_id)
        frame = frame[frame["road_id"].astype(str).str.upper() == road_key]
    if start:
        start_value = pd.Timestamp(start)
        start_value = start_value.tz_localize(None) if start_value.tzinfo else start_value
        frame = frame[frame["timestamp"] >= start_value]
    if end:
        end_value = pd.Timestamp(end)
        end_value = end_value.tz_localize(None) if end_value.tzinfo else end_value
        frame = frame[frame["timestamp"] <= end_value]
    records = frame.sort_values("timestamp", ascending=False).head(limit).copy()
    return [
        {
            "road_id": str(row["road_id"]),
            "timestamp": pd.Timestamp(row["timestamp"]).isoformat(),
            "vehicle_count": int(row["vehicle_count"]),
            "density": _density_from_row(row),
            "average_speed": float(row["average_speed"]),
            "congestion_level": _normalize_congestion_level(row.get("congestion_level")),
        }
        for _, row in records.iterrows()
    ]


@api_v1_router.get("/traffic/aggregate")
def get_traffic_aggregate(
    road_id: Optional[str] = None,
    granularity: str = Query(default="hour", pattern="^(hour|day)$"),
):
    frame = _load_traffic_data()
    if road_id:
        road_key = normalize_road_id(road_id)
        frame = frame[frame["road_id"].astype(str).str.upper() == road_key]
    if frame.empty:
        raise HTTPException(status_code=404, detail=f"Road {road_id} not found")
    bucket_frequency = "h" if granularity == "hour" else "D"
    frame = frame.copy()
    frame["bucket_at"] = pd.to_datetime(frame["timestamp"]).dt.floor(bucket_frequency)
    frame["congestion_level"] = frame["congestion_level"].apply(_normalize_congestion_level)
    grouped = frame.groupby(["road_id", "bucket_at"], sort=True)
    return [
        {
            "road_id": str(key[0]),
            "bucket": pd.Timestamp(key[1]).isoformat(),
            "avg_vehicle_count": round(float(group["vehicle_count"].mean()), 1),
            "avg_density": round(float(group.apply(_density_from_row, axis=1).mean()), 2),
            "avg_speed": round(float(group["average_speed"].mean()), 1),
            "dominant_congestion_level": str(group["congestion_level"].mode().iloc[0]),
            "sample_count": int(len(group)),
        }
        for key, group in grouped
    ]


@api_v1_router.get("/traffic/road-condition/{road_id}")
def get_road_condition(road_id: str):
    return _road_condition_data(road_id)


@api_v1_router.get("/analytics/trends")
def get_traffic_trends(
    road_id: str = "R001",
    range_name: str = Query(default="day", alias="range", pattern="^(day|week|month)$"),
):
    road_key = normalize_road_id(road_id)
    frame = _load_traffic_data()
    frame = frame[frame["road_id"].astype(str).str.upper() == road_key]
    if frame.empty:
        raise HTTPException(status_code=404, detail=f"Road {road_key} not found")
    frame = _history_in_range(frame, range_name)
    timestamps = pd.to_datetime(frame["timestamp"])
    if range_name == "day":
        frame["period"] = timestamps.dt.strftime("%H:00")
        period_order = [f"{hour:02d}:00" for hour in range(24)]
    elif range_name == "week":
        frame["period"] = timestamps.dt.day_name()
        period_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    else:
        frame["period"] = timestamps.dt.strftime("%Y-%m-%d")
        period_order = sorted(frame["period"].unique())
    points = []
    for period in period_order:
        group = frame[frame["period"] == period]
        if group.empty:
            continue
        points.append({
            "period": period,
            "avg_congestion": round(float(group["congestion_level"].map(_congestion_score).mean()), 3),
            "avg_speed": round(float(group["average_speed"].mean()), 2),
            "avg_density": round(float(group.apply(_density_from_row, axis=1).mean()), 3),
            "avg_vehicle_count": round(float(group["vehicle_count"].mean()), 1),
            "sample_count": int(len(group)),
        })
    return {"road_id": road_key, "range": range_name, "points": points, "data_source": TRAFFIC_DATA.source_name()}


@api_v1_router.get("/analytics/heatmap")
def get_traffic_heatmap(range_name: str = Query(default="day", alias="range", pattern="^(day|week)$")):
    frame = _history_in_range(_load_traffic_data(), range_name)
    roads = sorted(frame["road_id"].astype(str).unique().tolist())
    time_buckets = [f"{hour:02d}:00" for hour in range(24)]
    values = []
    sample_counts = []
    frame = frame.copy()
    frame["hour"] = pd.to_datetime(frame["timestamp"]).dt.strftime("%H:00")
    frame["score"] = frame["congestion_level"].map(_congestion_score)
    for road in roads:
        road_rows = frame[frame["road_id"].astype(str) == road]
        road_values = []
        road_counts = []
        for hour in time_buckets:
            bucket = road_rows[road_rows["hour"] == hour]
            road_values.append(round(float(bucket["score"].mean()), 3) if not bucket.empty else None)
            road_counts.append(int(len(bucket)))
        values.append(road_values)
        sample_counts.append(road_counts)
    return {
        "roads": roads,
        "time_buckets": time_buckets,
        "values": values,
        "sample_counts": sample_counts,
        "updated_at": pd.Timestamp(frame["timestamp"].max()).isoformat(),
        "data_source": TRAFFIC_DATA.source_name(),
    }


@api_v1_router.get("/analytics/reports")
def get_analytics_report(
    range_name: str = Query(default="week", alias="range", pattern="^(day|week|month)$"),
    output_format: str = Query(default="csv", alias="format", pattern="^(csv|json)$"),
):
    frame = _history_in_range(_load_traffic_data(), range_name).sort_values("timestamp", ascending=False).head(50000).copy()
    report = frame.rename(columns={"timestamp": "recorded_at", "average_speed": "average_speed_kmph"})
    report_data = report[["road_id", "recorded_at", "vehicle_count", "average_speed_kmph", "density", "congestion_level"]]
    if output_format == "json":
        return {
            "range": range_name,
            "record_count": int(len(report_data)),
            "generated_at": datetime.utcnow().isoformat(timespec="seconds"),
            "data_source": TRAFFIC_DATA.source_name(),
            "data": report_data.assign(recorded_at=report_data["recorded_at"].astype(str)).to_dict(orient="records"),
        }
    output = io.StringIO()
    report_data.to_csv(output, index=False)
    filename = f"traffic_report_{range_name}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@api_v1_router.get("/route/conditions")
def get_route_conditions(road_id: str):
    return _road_condition_data(road_id)

app.include_router(api_v1_router)