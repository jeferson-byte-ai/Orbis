"""
Subscription and billing models
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class SubscriptionFeatures(BaseModel):
    """Features available per tier"""
    max_meeting_duration: int  # minutes
    max_participants: int
    recording_enabled: bool
    transcription_enabled: bool
    voice_cloning_enabled: bool
    custom_branding: bool
    priority_support: bool
    api_access: bool
    analytics_enabled: bool
    storage_gb: int


# Feature limits per tier
TIER_FEATURES = {
    SubscriptionTier.FREE: SubscriptionFeatures(
        max_meeting_duration=40,
        max_participants=3,
        recording_enabled=False,
        transcription_enabled=True,
        voice_cloning_enabled=True,
        custom_branding=False,
        priority_support=False,
        api_access=False,
        analytics_enabled=False,
        storage_gb=1
    ),
    SubscriptionTier.PRO: SubscriptionFeatures(
        max_meeting_duration=240,
        max_participants=25,
        recording_enabled=True,
        transcription_enabled=True,
        voice_cloning_enabled=True,
        custom_branding=False,
        priority_support=True,
        api_access=True,
        analytics_enabled=True,
        storage_gb=100
    ),
    SubscriptionTier.ENTERPRISE: SubscriptionFeatures(
        max_meeting_duration=480,
        max_participants=100,
        recording_enabled=True,
        transcription_enabled=True,
        voice_cloning_enabled=True,
        custom_branding=True,
        priority_support=True,
        api_access=True,
        analytics_enabled=True,
        storage_gb=1000
    )
}


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    id: UUID
    user_id: UUID
    tier: SubscriptionTier
    status: SubscriptionStatus
    features: SubscriptionFeatures
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class UpdateSubscriptionRequest(BaseModel):
    """Update subscription request"""
    tier: SubscriptionTier
    billing_interval: str = Field(default="monthly", pattern="^(monthly|yearly)$")


class UsageStats(BaseModel):
    """Usage statistics for current period"""
    meetings_count: int
    total_minutes: int
    recordings_count: int
    storage_used_gb: float
    api_calls: int