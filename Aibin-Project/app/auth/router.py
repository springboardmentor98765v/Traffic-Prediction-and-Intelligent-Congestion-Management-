"""
Authentication routes for register, login, refresh, and me.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..database import get_db
from ..models import User, RefreshToken
from ..schemas import UserCreate, UserResponse, UserLogin, TokenResponse, RefreshRequest, AccessTokenResponse, UserMeResponse
from .security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from .dependencies import get_current_user
import hashlib

def get_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user_in.password)
    # create new user
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(user_id=new_user.id)

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return tokens."""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    access_token = create_access_token(data={"user_id": user.id, "role": user.role})
    refresh_token = create_refresh_token(data={"user_id": user.id})
    
    # Store refresh token hash in db
    token_hash = get_token_hash(refresh_token)
    payload = decode_token(refresh_token)
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role
    )

@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(refresh_data: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh the access token using a valid refresh token."""
    payload = decode_token(refresh_data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    # Check if token matches any of the stored hashes for this user
    user_tokens = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()
    
    valid_token = False
    for t in user_tokens:
        if get_token_hash(refresh_data.refresh_token) == t.token_hash:
            valid_token = True
            break
            
    if not valid_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    access_token = create_access_token(data={"user_id": user.id, "role": user.role})
    return AccessTokenResponse(access_token=access_token)

@router.get("/me", response_model=UserMeResponse)
def me(current_user: User = Depends(get_current_user)):
    """Return details for the currently authenticated user."""
    return UserMeResponse(
        user_id=current_user.id,
        name=current_user.name,
        role=current_user.role
    )
