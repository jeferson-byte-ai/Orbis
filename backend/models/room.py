"""Room models"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    """Create room request"""
    name: Optional[str] = None
    max_participants: int = Field(default=100, ge=2, le=100)
    pin: Optional[str] = Field(default=None, max_length=100)
    input_language: str = Field(default="auto")
    output_language: str = Field(default="auto")
    voice_profile_id: Optional[UUID] = None


class RoomResponse(BaseModel):
    """Room response"""
    id: UUID
    name: Optional[str]
    creator_id: Optional[UUID]
    max_participants: int
    is_active: bool
    participant_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class JoinRoomRequest(BaseModel):
    """Join room request"""
    pin: Optional[str] = None
    input_language: str = Field(default="auto")
    output_language: str = Field(default="auto")
    voice_profile_id: Optional[UUID] = None


class UpdateRoomConfigRequest(BaseModel):
    """Update room configuration during meeting"""
    input_language: Optional[str] = None
    output_language: Optional[str] = None
    voice_profile_id: Optional[UUID] = None


class ParticipantResponse(BaseModel):
    """Participant response"""
    id: UUID
    user_id: UUID
    username: str
    input_language: str
    output_language: str
    voice_profile_name: Optional[str]
    joined_at: datetime
    
    class Config:
        from_attributes = True


class RoomDetailResponse(RoomResponse):
    """Detailed room response with participants"""
    participants: List[ParticipantResponse] = []
