from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "public"

    @field_validator('role')
    @classmethod
    def normalize_role(cls, v: str) -> str:
        return v.lower()

    @field_validator('password')
    @classmethod
    def saturate_password_length(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            return v[:72]
        return v

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    role: str