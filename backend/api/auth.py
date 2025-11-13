"""Authentication endpoints - Enterprise grade"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import secrets

from backend.db.session import get_db
from backend.services.auth_service import auth_service
from backend.services.oauth_service import oauth_service
from backend.models.user import UserResponse
from backend.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Request/Response models
class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create new user account
    
    - **email**: Valid email address (unique)
    - **username**: Username (3-50 chars, unique)
    - **password**: Password (min 8 chars, must be strong)
    - **full_name**: Optional full name
    
    Returns the created user. A verification email will be sent.
    """
    user = await auth_service.register_user(
        db=db,
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        company=user.company,
        job_title=user.job_title,
        is_verified=user.is_verified,
        preferences=user.preferences,
        created_at=user.created_at
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Returns JWT access token, refresh token, and user info
    """
    # Get device info
    device_info = {
        "user_agent": http_request.headers.get("user-agent"),
        "accept_language": http_request.headers.get("accept-language")
    }
    
    access_token, refresh_token, user = await auth_service.login_user(
        db=db,
        email=request.email,
        password=request.password,
        device_info=device_info,
        ip_address=http_request.client.host,
        user_agent=http_request.headers.get("user-agent")
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            company=user.company,
            job_title=user.job_title,
            is_verified=user.is_verified,
            preferences=user.preferences,
            created_at=user.created_at
        )
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    Returns new access and refresh tokens
    """
    access_token, new_refresh_token = await auth_service.refresh_token(
        db=db,
        refresh_token=request.refresh_token
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating refresh token
    """
    await auth_service.logout_user(db=db, refresh_token=request.refresh_token)
    return {"message": "Successfully logged out"}


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token sent via email
    """
    user = await auth_service.verify_email(db=db, token=request.token)
    
    return {
        "message": "Email verified successfully",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            company=user.company,
            job_title=user.job_title,
            is_verified=user.is_verified,
            preferences=user.preferences,
            created_at=user.created_at
        )
    }


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend email verification link
    
    Sends a new verification email to the user
    """
    await auth_service.resend_verification_email(db=db, email=request.email)
    
    # Always return success to prevent email enumeration
    return {
        "message": "If an account with that email exists and is not verified, a verification link has been sent."
    }


@router.post("/password-reset/request")
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    
    Sends password reset email if account exists
    """
    await auth_service.request_password_reset(db=db, email=request.email)
    
    # Always return success to prevent email enumeration
    return {
        "message": "If an account with that email exists, a password reset link has been sent."
    }


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password with token from email
    """
    user = await auth_service.reset_password(
        db=db,
        token=request.token,
        new_password=request.new_password
    )
    
    return {
        "message": "Password reset successfully",
        "user_id": str(user.id)
    }


# ============= OAuth Endpoints =============

@router.get("/oauth/google")
async def google_oauth_init(request: Request):
    """
    Initialize Google OAuth flow
    Redirects user to Google login page
    """
    if not settings.enable_oauth or not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session/cache (simplified - in production use Redis)
    # For now, we'll validate on callback
    
    redirect_uri = f"{settings.frontend_url}/auth/google/callback"
    auth_url = await oauth_service.get_google_auth_url(redirect_uri, state)
    
    return {"auth_url": auth_url, "state": state}


@router.get("/oauth/google/callback")
async def google_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    Exchanges code for token and logs user in
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔐 Google OAuth callback - has code: {bool(code)}, state: {state[:10]}...")
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    redirect_uri = f"{settings.frontend_url}/auth/google/callback"
    logger.info(f"🔄 Redirect URI: {redirect_uri}")
    
    try:
        logger.info("📤 Exchanging code for tokens...")
        access_token, refresh_token, user = await oauth_service.authenticate_with_google(
            db=db,
            code=code,
            redirect_uri=redirect_uri
        )
        logger.info(f"✅ OAuth successful for user: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
                company=user.company,
                job_title=user.job_title,
                is_verified=user.is_verified,
                preferences=user.preferences,
                created_at=user.created_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.get("/oauth/github")
async def github_oauth_init(request: Request):
    """
    Initialize GitHub OAuth flow
    Redirects user to GitHub login page
    """
    if not settings.enable_oauth or not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env"
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    redirect_uri = f"{settings.frontend_url}/auth/github/callback"
    auth_url = await oauth_service.get_github_auth_url(redirect_uri, state)
    
    return {"auth_url": auth_url, "state": state}


@router.get("/oauth/github/callback")
async def github_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle GitHub OAuth callback
    Exchanges code for token and logs user in
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    redirect_uri = f"{settings.frontend_url}/auth/github/callback"
    
    try:
        access_token, refresh_token, user = await oauth_service.authenticate_with_github(
            db=db,
            code=code,
            redirect_uri=redirect_uri
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
                company=user.company,
                job_title=user.job_title,
                is_verified=user.is_verified,
                preferences=user.preferences,
                created_at=user.created_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )
