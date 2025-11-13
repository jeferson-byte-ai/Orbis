"""
Billing and Subscription endpoints
Stripe integration for payments
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.session import get_db
from backend.db.models import User, Subscription
from backend.models.subscription import (
    SubscriptionTier,
    UpdateSubscriptionRequest,
    SubscriptionResponse,
    TIER_FEATURES
)
from backend.api.deps import get_current_user
from backend.config import settings

router = APIRouter(prefix="/api/billing", tags=["Billing"])


@router.get("/plans")
async def get_plans():
    """Get available subscription plans with features"""
    return {
        "plans": [
            {
                "tier": "free",
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "interval": "month",
                "features": TIER_FEATURES[SubscriptionTier.FREE].dict(),
                "limits": {
                    "meetings": "Unlimited",
                    "duration": "40 min/meeting",
                    "participants": "3",
                    "storage": "1 GB"
                }
            },
            {
                "tier": "pro",
                "name": "Professional",
                "price": 19.99,
                "currency": "USD",
                "interval": "month",
                "features": TIER_FEATURES[SubscriptionTier.PRO].dict(),
                "limits": {
                    "meetings": "Unlimited",
                    "duration": "4 hours/meeting",
                    "participants": "25",
                    "storage": "100 GB"
                },
                "annual_price": 199.99,
                "annual_savings": 40
            },
            {
                "tier": "enterprise",
                "name": "Enterprise",
                "price": 99.99,
                "currency": "USD",
                "interval": "month",
                "features": TIER_FEATURES[SubscriptionTier.ENTERPRISE].dict(),
                "limits": {
                    "meetings": "Unlimited",
                    "duration": "8 hours/meeting",
                    "participants": "100",
                    "storage": "1 TB"
                },
                "annual_price": 999.99,
                "annual_savings": 200,
                "custom_options": True
            }
        ]
    }


@router.post("/checkout")
async def create_checkout_session(
    request: UpdateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription upgrade
    
    Returns checkout URL to redirect user to Stripe
    """
    # TODO: Implement actual Stripe integration
    # For now, return mock response
    
    if not settings.enable_payments:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )
    
    # Get or create subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        subscription = Subscription(
            user_id=current_user.id,
            tier=request.tier.value,
            status="trialing",
            trial_start=datetime.utcnow(),
            trial_end=datetime.utcnow() + timedelta(days=14),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.add(subscription)
        db.commit()
    
    # Mock Stripe checkout session
    checkout_url = f"{settings.frontend_url}/checkout?session_id=mock_session_123"
    
    return {
        "checkout_url": checkout_url,
        "session_id": "mock_session_123"
    }


@router.post("/portal")
async def create_portal_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe customer portal session
    
    Allows users to manage their subscription, update payment method, view invoices
    """
    if not settings.enable_payments:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )
    
    # TODO: Implement actual Stripe portal
    portal_url = f"{settings.frontend_url}/billing"
    
    return {
        "portal_url": portal_url
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription at period end
    
    User keeps access until end of billing period
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    if subscription.tier == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel free plan"
        )
    
    subscription.cancel_at_period_end = True
    subscription.cancelled_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Subscription will be cancelled at period end",
        "access_until": subscription.current_period_end
    }


@router.post("/reactivate")
async def reactivate_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate a cancelled subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription or not subscription.cancel_at_period_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No cancelled subscription found"
        )
    
    subscription.cancel_at_period_end = False
    subscription.cancelled_at = None
    
    db.commit()
    
    return {
        "message": "Subscription reactivated successfully"
    }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stripe webhook endpoint
    
    Handles subscription events from Stripe
    """
    # TODO: Implement actual Stripe webhook handling
    # Verify signature, process events
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Mock response
    return {"received": True}