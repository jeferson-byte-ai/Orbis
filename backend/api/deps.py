"""API dependencies - authentication, database, etc."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.models import User
from backend.core.security import decode_token
from backend.core.exceptions import AuthenticationError
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token authentication
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    logger.info(f"🔑 get_current_user called - has credentials: {bool(credentials)}")
    
    token = credentials.credentials
    logger.info(f"🎫 Token length: {len(token) if token else 0}")
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        logger.error("❌ Token decode failed - invalid or expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user ID from payload
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    # Convert user_id to UUID if it's a string
    try:
        if isinstance(user_id, str):
            import uuid as uuid_lib
            user_id = uuid_lib.UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid user ID format")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (can add additional checks here)
    """
    logger.info(f"✅ get_current_active_user - user: {current_user.email}")
    # Add any additional checks (e.g., is_active, email_verified, etc.)
    return current_user


# Optional auth - returns None if not authenticated
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except:
        return None


async def get_current_user_ws(websocket) -> Optional[User]:
    """
    Get current user from WebSocket connection
    Extracts token from query parameters or headers
    """
    from fastapi import WebSocket
    from backend.db.session import SessionLocal
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Try to get token from query params
    token = websocket.query_params.get("token")
    logger.info(f"🔑 Token from query params: {'Present' if token else 'Missing'}")
    
    if not token:
        # Try to get from headers
        token = websocket.headers.get("authorization")
        if token and token.startswith("Bearer "):
            token = token[7:]
        logger.info(f"🔑 Token from headers: {'Present' if token else 'Missing'}")
    
    if not token:
        logger.error("❌ No token found in query params or headers")
        return None
    
    logger.info(f"🔓 Decoding token (length: {len(token)})")
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        logger.error("❌ Token decode failed")
        return None
    
    logger.info(f"✅ Token decoded successfully: {payload}")
    
    # Get user ID
    user_id = payload.get("sub")
    if not user_id:
        logger.error("❌ No 'sub' field in token payload")
        return None
    
    logger.info(f"👤 User ID from token: {user_id}")
    
    # Convert user_id to UUID if it's a string
    try:
        if isinstance(user_id, str):
            import uuid as uuid_lib
            user_id = uuid_lib.UUID(user_id)
            logger.info(f"✅ Converted user_id to UUID: {user_id}")
    except (ValueError, AttributeError) as e:
        logger.error(f"❌ Failed to convert user_id to UUID: {e}")
        return None
    
    # Get user from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            logger.info(f"✅ User found in database: {user.email}")
        else:
            logger.error(f"❌ User not found in database for ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return None
    finally:
        db.close()
