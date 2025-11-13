"""User endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from backend.db.session import get_db
from backend.db.models import User
from backend.models.user import UserResponse, UpdatePreferencesRequest, UserPreferences
from backend.api.deps import get_current_active_user
from backend.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/api/users", tags=["Users"])


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None


class UpdatePreferencesAllRequest(BaseModel):
    theme: Optional[str] = None
    primary_language: Optional[str] = None
    auto_detect_input: Optional[bool] = None
    auto_detect_output: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    meeting_reminders: Optional[bool] = None
    feature_updates: Optional[bool] = None
    microphone_volume: Optional[int] = None
    speaker_volume: Optional[int] = None
    echo_cancellation: Optional[bool] = None
    noise_suppression: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class DeleteAccountRequest(BaseModel):
    password: Optional[str] = Field(default=None, min_length=1)
    confirmation: str = Field(min_length=1)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    # Add is_oauth_user flag
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "bio": current_user.bio,
        "company": current_user.company,
        "job_title": current_user.job_title,
        "is_verified": current_user.is_verified,
        "is_oauth_user": current_user.password_hash is None,  # OAuth user if no password
        "speaks_languages": current_user.speaks_languages,
        "understands_languages": current_user.understands_languages,
        "preferences": current_user.preferences,
        "created_at": current_user.created_at
    }
    return UserResponse(**user_dict)


@router.get("/me/preferences", response_model=UserPreferences)
def get_user_preferences(current_user: User = Depends(get_current_active_user)):
    """
    Get user preferences
    """
    return UserPreferences(**current_user.preferences)


@router.patch("/me/preferences", response_model=UserPreferences)
def update_user_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences (partial update for language settings)
    """
    # Update preferences
    preferences = current_user.preferences.copy()
    
    if request.primary_language is not None:
        preferences["primary_language"] = request.primary_language
    if request.output_language is not None:
        preferences["output_language"] = request.output_language
    if request.auto_detect_input is not None:
        preferences["auto_detect_input"] = request.auto_detect_input
    if request.auto_detect_output is not None:
        preferences["auto_detect_output"] = request.auto_detect_output
    
    current_user.preferences = preferences
    db.commit()
    db.refresh(current_user)
    
    return UserPreferences(**preferences)


@router.put("/me/preferences/all")
def update_all_preferences(
    request: UpdatePreferencesAllRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update all user preferences (theme, notifications, audio/video)
    """
    preferences = current_user.preferences.copy() if current_user.preferences else {}
    
    # Theme & Language
    if request.theme is not None:
        preferences["theme"] = request.theme
    if request.primary_language is not None:
        preferences["primary_language"] = request.primary_language
    if request.auto_detect_input is not None:
        preferences["auto_detect_input"] = request.auto_detect_input
    if request.auto_detect_output is not None:
        preferences["auto_detect_output"] = request.auto_detect_output
    
    # Notifications
    if request.email_notifications is not None:
        preferences["email_notifications"] = request.email_notifications
    if request.push_notifications is not None:
        preferences["push_notifications"] = request.push_notifications
    if request.meeting_reminders is not None:
        preferences["meeting_reminders"] = request.meeting_reminders
    if request.feature_updates is not None:
        preferences["feature_updates"] = request.feature_updates
    
    # Audio & Video
    if request.microphone_volume is not None:
        preferences["microphone_volume"] = request.microphone_volume
    if request.speaker_volume is not None:
        preferences["speaker_volume"] = request.speaker_volume
    if request.echo_cancellation is not None:
        preferences["echo_cancellation"] = request.echo_cancellation
    if request.noise_suppression is not None:
        preferences["noise_suppression"] = request.noise_suppression
    
    current_user.preferences = preferences
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Preferences updated successfully", "preferences": preferences}


@router.put("/me/profile", response_model=UserResponse)
def update_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    """
    if request.full_name is not None:
        current_user.full_name = request.full_name
    
    if request.bio is not None:
        current_user.bio = request.bio
    
    if request.company is not None:
        current_user.company = request.company
    
    if request.job_title is not None:
        current_user.job_title = request.job_title
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.delete("/me")
def delete_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account permanently (irreversible!)
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🗑️ Delete account request for user: {current_user.email}")
    logger.info(f"📝 Request data - has password: {bool(request.password)}, confirmation: {request.confirmation}")
    
    # Check if user has a password (not OAuth user)
    if current_user.password_hash:
        # Regular user - verify password
        if not request.password:
            logger.error("❌ Password required but not provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required to delete your account"
            )
        
        if not verify_password(request.password, current_user.password_hash):
            logger.error("❌ Password verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect"
            )
    else:
        # OAuth user - no password needed
        logger.info("✅ OAuth user - skipping password verification")
    
    # Verify confirmation
    if request.confirmation.upper() != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please type DELETE to confirm account deletion"
        )
    
    # Delete user (cascade will delete related data)
    logger.info(f"✅ Deleting user {current_user.email}")
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}
