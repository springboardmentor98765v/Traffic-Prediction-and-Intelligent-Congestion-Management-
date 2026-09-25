from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLoginSchema
from app.security.password import hash_password, verify_password
from app.security.config import SECRET_KEY, ALGORITHM

import uuid

router = APIRouter(tags=["Authentication"])

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.name).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken. Please choose a different one.")
    
    hashed_pw = hash_password(user.password)
    
    # SECURE FIX: Hardcode role to "user" so public signups cannot choose admin/operator roles
    new_user = User(
        id=f"USR-{uuid.uuid4().hex[:8].upper()}",
        username=user.name,
        email=user.email,
        password_hash=hashed_pw,  
        role="user",
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
        
    return {"user_id": new_user.id, "message": "User registered successfully"}

@router.post("/login", status_code=200)
def login_user(user_credentials: UserLoginSchema, db: Session = Depends(get_db)):
    # Verify user exists in the database
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Map lowercase "user" to uppercase "PUBLIC" for frontend compliance
    frontend_role = "PUBLIC" if user.role == "user" else user.role

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": frontend_role
    }
    
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": frontend_role
    }

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh_access_token(request: RefreshRequest):
    credentials_exception = HTTPException(
        status_code=401, 
        detail="Invalid or expired refresh token"
    )
    try:
        payload = jwt.decode(
            request.refresh_token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        
        if payload.get("token_type") != "refresh":
            raise credentials_exception
            
        user_id = payload.get("sub")
        role = payload.get("role")
        username = payload.get("username")
        
        if user_id is None:
            raise credentials_exception
            
        new_token_data = {"sub": user_id, "username": username, "role": role}
        new_access_token = create_access_token(new_token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except Exception:
        raise credentials_exception

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") == "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type for this endpoint")
        
        user_id = payload.get("sub")
        role = payload.get("role")
        username = payload.get("username")
        
        if user_id is None:
            raise credentials_exception
            
        return {"user_id": user_id, "username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception:
        raise credentials_exception

@router.get("/me", status_code=200)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile and role details.
    Requires a valid Bearer token in the request header.
    """
    role = current_user["role"]
    if role == "user":
        role = "PUBLIC"
        
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "role": role
    }