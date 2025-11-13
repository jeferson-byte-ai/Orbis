"""User models"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, HttpUrl, Field


class UserPreferences(BaseModel):
    """User preferences"""
    primary_language: str = "en"
    output_language: str = "en"
    auto_detect_input: bool = True
    auto_detect_output: bool = True
    theme: str = "dark"
    notifications_enabled: bool = True
    email_notifications: bool = True


class UserResponse(BaseModel):
    """User response"""
    id: UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    is_verified: bool = False
    is_oauth_user: bool = False  # True if user logged in via OAuth (no password)
    speaks_languages: List[str] = ["en"]
    understands_languages: List[str] = ["en"]
    preferences: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None


class UpdatePreferencesRequest(BaseModel):
    """Update user preferences"""
    primary_language: Optional[str] = None
    output_language: Optional[str] = None
    auto_detect_input: Optional[bool] = None
    auto_detect_output: Optional[bool] = None
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None


class UpdateLanguagesRequest(BaseModel):
    """Update user languages"""
    speaks_languages: Optional[List[str]] = None
    understands_languages: Optional[List[str]] = None


class UserStats(BaseModel):
    """User statistics"""
    total_meetings: int
    total_minutes: int
    languages_used: int
    voice_profiles: int
    recordings: int
