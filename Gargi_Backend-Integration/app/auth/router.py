from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RefreshRequest,
    RefreshResponse,
)
from app.core.exceptions import conflict_error, unauthorized_error
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database.connection import get_db
from app.database.models import Role, User

router = APIRouter(prefix="/auth", tags=["Authentication"])


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        token = credentials.credentials

        payload = decode_token(token)

        if payload.get("type") != "access":
            raise unauthorized_error()

        user_id = payload.get("sub")

        if not user_id:
            raise unauthorized_error()

        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise unauthorized_error()

        return user

    except (JWTError, ValueError, TypeError):
        raise unauthorized_error()


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        raise conflict_error("Email already registered")

    role = db.query(Role).filter(Role.name == request.role).first()

    if not role:
        raise conflict_error("Invalid role")

    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role_id=role.id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user_id": user.id}


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise unauthorized_error()

    if not verify_password(request.password, user.password_hash):
        raise unauthorized_error()

    role = db.query(Role).filter(Role.id == user.role_id).first()

    if not role:
        raise unauthorized_error()

    access_token = create_access_token(user.id, role.name)

    refresh_token = create_refresh_token(user.id, role.name)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": role.name,
    }


@router.post("/refresh", response_model=RefreshResponse)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = decode_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise unauthorized_error()

        user_id = payload.get("sub")

        if not user_id:
            raise unauthorized_error()

        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise unauthorized_error()

        role = db.query(Role).filter(Role.id == user.role_id).first()

        if not role:
            raise unauthorized_error()

        access_token = create_access_token(user.id, role.name)

        return {"access_token": access_token}

    except (JWTError, ValueError, TypeError):
        raise unauthorized_error()


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    if not current_user.role:
        raise unauthorized_error()

    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "role": current_user.role.name,
    }
