"""
Authentication Service
Complete auth system with email/password, OAuth, password reset, email verification
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from backend.db.models import User, UserSession, PasswordReset, Subscription
from backend.services.email_service import email_service


class AuthService:
    """Authentication service"""
    
    @staticmethod
    async def register_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Register a new user
        """
        # Check if email exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username exists
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user (already verified - no email verification needed)
        user = User(
            email=email,
            username=username,
            password_hash=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_verified=True,  # Auto-verified
            email_verification_token=None
        )
        
        db.add(user)
        db.flush()
        
        # Create free subscription
        subscription = Subscription(
            user_id=user.id,
            tier="free",
            status="active",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.add(subscription)
        
        db.commit()
        db.refresh(user)
        
        # Send welcome email directly
        await email_service.send_welcome_email(
            email=user.email,
            username=user.username
        )
        
        return user
    
    @staticmethod
    async def login_user(
        db: Session,
        email: str,
        password: str,
        device_info: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str, User]:
        """
        Login user and create session
        Returns: (access_token, refresh_token, user)
        """
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Create session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(session)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        
        db.commit()
        
        return access_token, refresh_token, user
    
    @staticmethod
    async def logout_user(db: Session, refresh_token: str):
        """Logout user by invalidating session"""
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
    
    @staticmethod
    async def refresh_token(db: Session, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token
        Returns: (new_access_token, new_refresh_token)
        """
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        ).first()
        
        if not session or session.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": str(session.user_id)})
        new_refresh_token = create_refresh_token(data={"sub": str(session.user_id)})
        
        # Update session
        session.refresh_token = new_refresh_token
        session.last_activity = datetime.utcnow()
        session.expires_at = datetime.utcnow() + timedelta(days=7)
        
        db.commit()
        
        return access_token, new_refresh_token
    
    @staticmethod
    async def verify_email(db: Session, token: str) -> User:
        """Verify user email"""
        user = db.query(User).filter(
            User.email_verification_token == token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        user.is_verified = True
        user.email_verification_token = None
        
        db.commit()
        db.refresh(user)
        
        # Send welcome email
        await email_service.send_welcome_email(
            email=user.email,
            username=user.username
        )
        
        return user
    
    @staticmethod
    async def resend_verification_email(db: Session, email: str):
        """Resend verification email"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists
            return
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Generate new token if needed
        if not user.email_verification_token:
            user.email_verification_token = secrets.token_urlsafe(32)
            db.commit()
        
        # Send verification email
        await email_service.send_verification_email(
            email=user.email,
            username=user.username,
            token=user.email_verification_token
        )
    
    @staticmethod
    async def request_password_reset(db: Session, email: str):
        """Request password reset"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists
            return
        
        # Create reset token
        token = secrets.token_urlsafe(32)
        reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(reset)
        db.commit()
        
        # Send reset email
        await email_service.send_password_reset_email(
            email=user.email,
            username=user.username,
            token=token
        )
    
    @staticmethod
    async def reset_password(db: Session, token: str, new_password: str) -> User:
        """Reset password with token"""
        reset = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.is_used == False,
            PasswordReset.expires_at > datetime.utcnow()
        ).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password
        user = db.query(User).filter(User.id == reset.user_id).first()
        user.password_hash = get_password_hash(new_password)
        
        # Mark token as used
        reset.is_used = True
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    async def change_password(
        db: Session,
        user_id: UUID,
        current_password: str,
        new_password: str
    ):
        """Change user password"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        user.password_hash = get_password_hash(new_password)
        db.commit()
    
    @staticmethod
    async def oauth_login(
        db: Session,
        provider: str,
        provider_user_id: str,
        email: str,
        username: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Tuple[str, str, User]:
        """
        Login/register via OAuth provider
        """
        # Check if user exists
        is_new_user = False
        
        if provider == "google":
            user = db.query(User).filter(User.google_id == provider_user_id).first()
        elif provider == "github":
            user = db.query(User).filter(User.github_id == provider_user_id).first()
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        
        # If not found by provider ID, try email
        if not user:
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                # Link OAuth account
                if provider == "google":
                    user.google_id = provider_user_id
                elif provider == "github":
                    user.github_id = provider_user_id
            else:
                # Create new user
                is_new_user = True
                user = User(
                    email=email,
                    username=username,
                    full_name=full_name,
                    avatar_url=avatar_url,
                    is_active=True,
                    is_verified=True,  # OAuth emails are pre-verified
                    password_hash=None  # No password for OAuth users
                )
                
                if provider == "google":
                    user.google_id = provider_user_id
                elif provider == "github":
                    user.github_id = provider_user_id
                
                db.add(user)
                db.flush()
                
                # Create free subscription
                subscription = Subscription(
                    user_id=user.id,
                    tier="free",
                    status="active",
                    current_period_end=datetime.utcnow() + timedelta(days=30)
                )
                db.add(subscription)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Create session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(session)
        
        db.commit()
        db.refresh(user)
        
        # Send welcome email for new OAuth users
        if is_new_user:
            await email_service.send_welcome_email(
                email=user.email,
                username=user.username
            )
        
        return access_token, refresh_token, user


auth_service = AuthService()