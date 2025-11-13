"""API Key models for programmatic access"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class APIKeyCreate(BaseModel):
    """Request to create API key"""
    name: str = Field(min_length=1, max_length=100, description="Friendly name for the key")
    scopes: List[str] = Field(default=["read"], description="Permissions for this key")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")


class APIKeyResponse(BaseModel):
    """API Key response (without secret)"""
    id: UUID
    name: str
    prefix: str  # First 8 chars of key for identification
    scopes: List[str]
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeyWithSecret(BaseModel):
    """Full API key with secret (only shown on creation)"""
    id: UUID
    name: str
    key: str  # Full API key - ONLY shown once!
    scopes: List[str]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeyUpdate(BaseModel):
    """Update API key"""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    scopes: Optional[List[str]] = None
