"""Custom exceptions"""
from fastapi import HTTPException, status


class OrbisException(HTTPException):
    """Base exception for Orbis"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationError(OrbisException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(OrbisException):
    """Not authorized"""
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(OrbisException):
    """Resource not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(OrbisException):
    """Validation error"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class RateLimitError(OrbisException):
    """Rate limit exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail=detail, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class RoomFullError(OrbisException):
    """Room is full"""
    def __init__(self, detail: str = "Room is full"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class VoiceNotReadyError(OrbisException):
    """Voice profile not ready"""
    def __init__(self, detail: str = "Voice profile is still being prepared"):
        super().__init__(detail=detail, status_code=status.HTTP_425_TOO_EARLY)
