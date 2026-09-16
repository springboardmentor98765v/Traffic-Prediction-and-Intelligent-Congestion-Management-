from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    operator = "operator"
    public = "public"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    role: RoleEnum = RoleEnum.public

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if "admin" in v_clean:
                return RoleEnum.admin
            elif "operator" in v_clean:
                return RoleEnum.operator
            elif "public" in v_clean or "commuter" in v_clean:
                return RoleEnum.public
        return v


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
