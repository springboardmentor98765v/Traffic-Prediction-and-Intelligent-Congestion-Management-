import os
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import DateTime, ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trafficvision.db")
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-me")
ALGORITHM = "HS256"
ACCESS_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()


class Base(DeclarativeBase):
    pass


class Role(str, Enum):
    admin = "admin"
    traffic_operator = "traffic_operator"
    public = "public"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SessionToken(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    refresh_token_jti: Mapped[str] = mapped_column(String(36), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def issue_token(user: User, token_type: str, expires_delta: timedelta, jti: str | None = None) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": user.id, "role": user.role, "type": token_type, "iat": now, "exp": now + expires_delta, "jti": jti or str(uuid.uuid4())}, JWT_SECRET, algorithm=ALGORITHM)


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise JWTError
        user = db.get(User, payload.get("sub"))
    except JWTError:
        user = None
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")
    return user


def require_roles(*allowed: Role):
    def checker(user: User = Depends(current_user)) -> User:
        if user.role not in {role.value for role in allowed}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user
    return checker


app = FastAPI(title="TrafficVision AI Authentication Service", version="1.0.0")


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}


@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=payload.name, email=payload.email.lower(), password_hash=pwd_context.hash(payload.password), role=payload.role.value)
    db.add(user); db.commit(); db.refresh(user)
    return {"user_id": user.id}


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    jti = str(uuid.uuid4())
    db.add(SessionToken(user_id=user.id, refresh_token_jti=jti, expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_DAYS)))
    db.commit()
    return {"access_token": issue_token(user, "access", timedelta(minutes=ACCESS_MINUTES)), "refresh_token": issue_token(user, "refresh", timedelta(days=REFRESH_DAYS), jti), "role": user.role}


@app.post("/api/v1/auth/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        claims = jwt.decode(payload.refresh_token, JWT_SECRET, algorithms=[ALGORITHM])
        if claims.get("type") != "refresh": raise JWTError
        token_session = db.query(SessionToken).filter(SessionToken.refresh_token_jti == claims.get("jti"), SessionToken.revoked_at.is_(None)).first()
        user = db.get(User, claims.get("sub"))
    except JWTError:
        token_session = user = None
    if not token_session or not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return {"access_token": issue_token(user, "access", timedelta(minutes=ACCESS_MINUTES))}


@app.get("/api/v1/auth/me")
def me(user: User = Depends(current_user)):
    return {"user_id": user.id, "name": user.name, "role": user.role}


@app.get("/api/v1/admin/health")
def admin_health(_: User = Depends(require_roles(Role.admin))):
    return {"status": "ok"}
