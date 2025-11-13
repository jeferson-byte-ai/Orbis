"""
Security API Endpoints
2FA, API Keys, Security Events
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.api.deps import get_current_user, get_db
from backend.db.models import User
from backend.db.models_security import (
    TwoFactorAuth, APIKeySecure, SecurityEvent, PasswordHistory
)
from backend.core.security_enhanced import (
    two_factor_service,
    api_key_service,
    password_security_service,
    security_event_logger
)
from backend.core.encryption import encryption_service
from backend.core.security import get_password_hash, verify_password


router = APIRouter(prefix="/api/security", tags=["security"])


# ============================================
# 2FA Endpoints
# ============================================

class Enable2FARequest(BaseModel):
    password: str


class Verify2FARequest(BaseModel):
    code: str


class Disable2FARequest(BaseModel):
    password: str
    code: str


@router.post("/2fa/enable")
async def enable_2fa(
    request: Enable2FARequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable 2FA - Step 1: Generate secret and QR code
    """
    # Verify password
    if not verify_password(request.password, current_user.password_hash):
        await security_event_logger.log_event(
            db, "2fa_enable_failed", "medium",
            "Failed 2FA enable attempt - wrong password",
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Check if 2FA already enabled
    existing_2fa = db.query(TwoFactorAuth).filter(
        TwoFactorAuth.user_id == current_user.id
    ).first()
    
    if existing_2fa and existing_2fa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    # Generate secret
    secret = two_factor_service.generate_secret()
    
    # Encrypt secret for storage
    secret_encrypted, secret_nonce = encryption_service.encrypt_string(secret)
    
    # Generate backup codes
    backup_codes = two_factor_service.generate_backup_codes()
    backup_codes_hashed = two_factor_service.hash_backup_codes(backup_codes)
    
    # Store in database
    if existing_2fa:
        existing_2fa.totp_secret_encrypted = secret_encrypted
        existing_2fa.totp_secret_nonce = secret_nonce
        existing_2fa.backup_codes = backup_codes_hashed
        existing_2fa.is_enabled = False  # Will be enabled after verification
        existing_2fa.is_verified = False
    else:
        two_factor = TwoFactorAuth(
            user_id=current_user.id,
            totp_secret_encrypted=secret_encrypted,
            totp_secret_nonce=secret_nonce,
            backup_codes=backup_codes_hashed,
            is_enabled=False,
            is_verified=False
        )
        db.add(two_factor)
    
    db.commit()
    
    # Generate QR code
    qr_code_bytes = two_factor_service.generate_qr_code(secret, current_user.email)
    
    await security_event_logger.log_event(
        db, "2fa_setup_started", "low",
        "User started 2FA setup",
        user_id=str(current_user.id)
    )
    
    return {
        "secret": secret,  # Show once for manual entry
        "qr_code": f"data:image/png;base64,{__import__('base64').b64encode(qr_code_bytes).decode()}",
        "backup_codes": backup_codes,  # Show once!
        "message": "Scan QR code with authenticator app and verify with code"
    }


@router.post("/2fa/verify")
async def verify_2fa_setup(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable 2FA - Step 2: Verify code and activate
    """
    two_factor = db.query(TwoFactorAuth).filter(
        TwoFactorAuth.user_id == current_user.id
    ).first()
    
    if not two_factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="2FA setup not started"
        )
    
    # Decrypt secret
    secret = encryption_service.decrypt_string(
        two_factor.totp_secret_encrypted,
        two_factor.totp_secret_nonce
    )
    
    # Verify code
    if not two_factor_service.verify_code(secret, request.code):
        await security_event_logger.log_event(
            db, "2fa_verify_failed", "medium",
            "Failed 2FA verification",
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Enable 2FA
    two_factor.is_enabled = True
    two_factor.is_verified = True
    two_factor.verified_at = datetime.utcnow()
    db.commit()
    
    await security_event_logger.log_event(
        db, "2fa_enabled", "low",
        "2FA successfully enabled",
        user_id=str(current_user.id)
    )
    
    return {"message": "2FA enabled successfully", "status": "enabled"}


@router.post("/2fa/disable")
async def disable_2fa(
    request: Disable2FARequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA"""
    # Verify password
    if not verify_password(request.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    two_factor = db.query(TwoFactorAuth).filter(
        TwoFactorAuth.user_id == current_user.id
    ).first()
    
    if not two_factor or not two_factor.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    # Decrypt and verify code
    secret = encryption_service.decrypt_string(
        two_factor.totp_secret_encrypted,
        two_factor.totp_secret_nonce
    )
    
    if not two_factor_service.verify_code(secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Disable 2FA
    db.delete(two_factor)
    db.commit()
    
    await security_event_logger.log_event(
        db, "2fa_disabled", "medium",
        "2FA disabled",
        user_id=str(current_user.id)
    )
    
    return {"message": "2FA disabled successfully"}


@router.get("/2fa/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get 2FA status"""
    two_factor = db.query(TwoFactorAuth).filter(
        TwoFactorAuth.user_id == current_user.id
    ).first()
    
    return {
        "enabled": two_factor.is_enabled if two_factor else False,
        "verified": two_factor.is_verified if two_factor else False,
        "method": two_factor.method if two_factor else None
    }


# ============================================
# API Key Management
# ============================================

class CreateAPIKeyRequest(BaseModel):
    name: str
    description: Optional[str] = None
    scopes: Optional[List[str]] = None
    expires_days: Optional[int] = None


@router.post("/api-keys")
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    # Generate key
    full_key, key_hash, key_prefix = api_key_service.generate_api_key()
    
    # Calculate expiration
    expires_at = None
    if request.expires_days:
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(days=request.expires_days)
    
    # Store in database
    api_key = APIKeySecure(
        user_id=current_user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=request.name,
        description=request.description,
        scopes=__import__('json').dumps(request.scopes or []),
        expires_at=expires_at
    )
    
    db.add(api_key)
    db.commit()
    
    await security_event_logger.log_event(
        db, "api_key_created", "low",
        f"API key created: {request.name}",
        user_id=str(current_user.id)
    )
    
    return {
        "api_key": full_key,  # ONLY shown once!
        "key_prefix": key_prefix,
        "name": request.name,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "warning": "Save this key now. You won't be able to see it again!"
    }


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all API keys (without revealing actual keys)"""
    keys = db.query(APIKeySecure).filter(
        APIKeySecure.user_id == current_user.id,
        APIKeySecure.is_active == True
    ).all()
    
    return [
        {
            "id": str(key.id),
            "key_prefix": key.key_prefix,
            "name": key.name,
            "description": key.description,
            "created_at": key.created_at,
            "last_used_at": key.last_used_at,
            "expires_at": key.expires_at,
            "total_requests": key.total_requests
        }
        for key in keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke an API key"""
    api_key = db.query(APIKeySecure).filter(
        APIKeySecure.id == key_id,
        APIKeySecure.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    api_key.revoked_at = datetime.utcnow()
    db.commit()
    
    await security_event_logger.log_event(
        db, "api_key_revoked", "low",
        f"API key revoked: {api_key.name}",
        user_id=str(current_user.id)
    )
    
    return {"message": "API key revoked successfully"}


# ============================================
# Security Events & Audit
# ============================================

@router.get("/events")
async def get_security_events(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent security events for current user"""
    events = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == current_user.id
    ).order_by(SecurityEvent.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": str(event.id),
            "event_type": event.event_type,
            "severity": event.severity,
            "description": event.description,
            "ip_address": event.ip_address,
            "created_at": event.created_at,
            "resolved": event.resolved
        }
        for event in events
    ]


# ============================================
# Password Security
# ============================================

class CheckPasswordRequest(BaseModel):
    password: str


@router.post("/password/check-breach")
async def check_password_breach(
    request: CheckPasswordRequest,
    current_user: User = Depends(get_current_user)
):
    """Check if password has been in a data breach"""
    is_breached, times_seen = await password_security_service.check_password_breach(
        request.password
    )
    
    return {
        "is_breached": is_breached,
        "times_seen": times_seen,
        "safe": not is_breached,
        "recommendation": "Choose a different password" if is_breached else "Password looks safe"
    }


@router.post("/password/check-strength")
async def check_password_strength(
    request: CheckPasswordRequest,
    current_user: User = Depends(get_current_user)
):
    """Check password strength"""
    is_valid, issues, score = password_security_service.validate_password_strength(
        request.password
    )
    
    strength_label = "weak"
    if score >= 8:
        strength_label = "very strong"
    elif score >= 6:
        strength_label = "strong"
    elif score >= 4:
        strength_label = "moderate"
    
    return {
        "is_valid": is_valid,
        "issues": issues,
        "score": score,
        "strength": strength_label
    }
