"""Voice profile models"""
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class VoiceProfileResponse(BaseModel):
    """Voice profile response"""
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )
    
    id: UUID
    user_id: UUID
    type: Literal["cloned", "preset"]
    name: str
    language: str
    model_path: Optional[str]
    quality_score: Optional[float]
    is_default: bool
    is_ready: bool
    training_progress: float
    created_at: datetime


class VoiceCloneRequest(BaseModel):
    """Voice clone request metadata"""
    name: str = Field(default="My Voice", max_length=255)
    language: str = Field(default="en", pattern="^[a-z]{2}$")


class VoiceCloneStatusResponse(BaseModel):
    """Voice clone status"""
    id: UUID
    is_ready: bool
    training_progress: float
    estimated_completion_seconds: Optional[int] = None


class PresetVoice(BaseModel):
    """Preset voice info"""
    id: str
    name: str
    language: str
    gender: Literal["male", "female", "neutral"]
    description: str
    sample_url: Optional[str] = None


class SetDefaultVoiceRequest(BaseModel):
    """Set default voice"""
    voice_id: UUID
