"""Authentication request/response models"""
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
