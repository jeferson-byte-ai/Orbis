"""Security utilities - password hashing, JWT tokens, etc."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔓 Attempting to decode token (length: {len(token)})")
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        logger.info(f"✅ Token decoded successfully - sub: {payload.get('sub')}, type: {payload.get('type')}, exp: {payload.get('exp')}")
        return payload
    except JWTError as e:
        logger.error(f"❌ JWT decode error: {str(e)}")
        return None


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength
    Returns: (is_valid, list_of_issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one number")
    
    return (len(issues) == 0, issues)


async def verify_api_key(api_key: str):
    """
    Verify API key and return associated user
    """
    from backend.db.session import SessionLocal
    from backend.db.models import User, APIKey
    
    db = SessionLocal()
    try:
        # Get API key from database
        key = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active == True).first()
        if not key:
            return None
        
        # Get associated user
        user = db.query(User).filter(User.id == key.user_id).first()
        return user
    finally:
        db.close()
