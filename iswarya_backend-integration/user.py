from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum

# 1. Define the allowed roles here
class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    operator = "operator"

# 2. Update the role field inside your schema
class UserCreate(BaseModel):
    name: str
    email: EmailStr  
    password: str
    role: UserRole = UserRole.user  

    @field_validator('email')
    @classmethod
    def validate_and_normalize_email(cls, v: str) -> str:
        v = v.lower().strip()
        
        # Split the email into username and domain
        parts = v.split("@")
        if len(parts) != 2:
            raise ValueError("Invalid email format.")
        
        username, domain = parts
        
        # Catch any variation of gmail typos (e.g., gamil, gmal, gafsdfmil, etc.)
        if "g" in domain and "mil" in domain and domain != "gmail.com":
            raise ValueError("Invalid email domain typo detected. Did you mean @gmail.com?")
            
        # Restrict to trusted providers
        allowed_domains = ["gmail.com", "yahoo.com", "outlook.com", "nitpy.ac.in"]
        if domain not in allowed_domains:
            raise ValueError(f"Registration is restricted. Domain '@{domain}' is not supported.")
            
        return v

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
    role: UserRole