"""
Security Middleware
Implements security headers, CSRF protection, and security best practices
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import Response
from typing import Callable
import secrets
import hashlib
from backend.config import settings
from backend.core.cache import cache_service
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response: Response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS (HTTP Strict Transport Security)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "media-src 'self' blob:",
            "connect-src 'self' wss: ws:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Permissions Policy (formerly Feature Policy)
        permissions = [
            "geolocation=()",
            "microphone=(self)",
            "camera=(self)",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "speaker=(self)"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)
        
        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF Protection for state-changing operations"""
    
    def __init__(self, app):
        super().__init__(app)
        self.csrf_cookie_name = "csrf_token"
        self.csrf_header_name = "X-CSRF-Token"
        self.safe_methods = {"GET", "HEAD", "OPTIONS"}
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip CSRF check for safe methods and API keys
        if request.method in self.safe_methods:
            response = await call_next(request)
            # Set CSRF token cookie on GET requests
            if request.method == "GET":
                csrf_token = self._generate_csrf_token()
                response.set_cookie(
                    key=self.csrf_cookie_name,
                    value=csrf_token,
                    httponly=True,
                    secure=settings.is_production,
                    samesite="strict",
                    max_age=3600  # 1 hour
                )
            return response
        
        # Skip for WebSocket endpoints
        if request.url.path.startswith("/ws/"):
            return await call_next(request)
        
        # Skip for API key authentication
        if "X-API-Key" in request.headers:
            return await call_next(request)
        
        # Verify CSRF token
        csrf_cookie = request.cookies.get(self.csrf_cookie_name)
        csrf_header = request.headers.get(self.csrf_header_name)
        
        if not csrf_cookie or not csrf_header:
            logger.warning(
                f"CSRF check failed: missing token - "
                f"IP: {request.client.host}, Path: {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        if not secrets.compare_digest(csrf_cookie, csrf_header):
            logger.warning(
                f"CSRF check failed: invalid token - "
                f"IP: {request.client.host}, Path: {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )
        
        return await call_next(request)
    
    def _generate_csrf_token(self) -> str:
        """Generate secure CSRF token"""
        return secrets.token_urlsafe(32)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelisting for admin endpoints"""
    
    def __init__(self, app, admin_paths: list = None):
        super().__init__(app)
        self.admin_paths = admin_paths or ["/admin", "/api/admin"]
        self.whitelisted_ips = set(
            ip.strip() for ip in 
            settings.__dict__.get("admin_whitelist_ips", "").split(",")
            if ip.strip()
        )
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check if path requires IP whitelist
        requires_whitelist = any(
            request.url.path.startswith(path) for path in self.admin_paths
        )
        
        if requires_whitelist and self.whitelisted_ips:
            client_ip = self._get_client_ip(request)
            
            if client_ip not in self.whitelisted_ips:
                logger.warning(
                    f"Unauthorized admin access attempt from IP: {client_ip} "
                    f"to path: {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP (handles proxies)"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID for tracing"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate or use existing request ID
        request_id = request.headers.get("X-Request-ID") or secrets.token_urlsafe(16)
        
        # Store in request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate request size and content"""
    
    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check request body size
        if request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.headers.get("Content-Length")
            
            if content_length:
                content_length = int(content_length)
                
                if content_length > self.max_body_size:
                    logger.warning(
                        f"Request body too large: {content_length} bytes from "
                        f"IP: {request.client.host}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request body too large. Maximum size: {self.max_body_size} bytes"
                    )
        
        return await call_next(request)


class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    """Basic SQL injection detection"""
    
    # Common SQL injection patterns
    SQL_PATTERNS = [
        "union select",
        "drop table",
        "insert into",
        "delete from",
        "update set",
        "exec(",
        "execute(",
        "--",
        "/*",
        "xp_",
        "sp_"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check query parameters
        query_string = str(request.url.query).lower()
        
        for pattern in self.SQL_PATTERNS:
            if pattern in query_string:
                logger.error(
                    f"Potential SQL injection detected: {pattern} in query "
                    f"from IP: {request.client.host}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request"
                )
        
        return await call_next(request)


class BruteForceProtectionMiddleware(BaseHTTPMiddleware):
    """Protect against brute force attacks"""
    
    def __init__(
        self,
        app,
        max_attempts: int = 5,
        lockout_duration: int = 300  # 5 minutes
    ):
        super().__init__(app)
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.protected_paths = ["/api/auth/login", "/api/auth/signup"]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check if path is protected
        if request.url.path in self.protected_paths:
            ip = request.client.host
            key = f"brute_force:{ip}:{request.url.path}"
            
            # Check if IP is locked out
            lockout_key = f"{key}:locked"
            is_locked = await cache_service.exists(lockout_key)
            
            if is_locked:
                logger.warning(f"Blocked brute force attempt from locked IP: {ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed attempts. Please try again later."
                )
        
        # Process request
        response = await call_next(request)
        
        # Track failed attempts
        if (request.url.path in self.protected_paths and 
            response.status_code in [401, 403]):
            
            ip = request.client.host
            key = f"brute_force:{ip}:{request.url.path}"
            
            # Increment attempts
            attempts = await cache_service.increment(key)
            if attempts == 1:
                # Set expiration on first attempt
                await cache_service.expire(key, self.lockout_duration)
            
            # Lock if max attempts reached
            if attempts and attempts >= self.max_attempts:
                lockout_key = f"{key}:locked"
                await cache_service.set(
                    lockout_key,
                    True,
                    ttl=self.lockout_duration
                )
                logger.warning(
                    f"IP {ip} locked out after {attempts} failed attempts "
                    f"on {request.url.path}"
                )
        
        # Clear attempts on successful auth
        elif (request.url.path in self.protected_paths and 
              response.status_code == 200):
            ip = request.client.host
            key = f"brute_force:{ip}:{request.url.path}"
            await cache_service.delete(key)
        
        return response


def calculate_checksum(data: bytes) -> str:
    """Calculate SHA-256 checksum for data integrity"""
    return hashlib.sha256(data).hexdigest()


def verify_checksum(data: bytes, expected_checksum: str) -> bool:
    """Verify data integrity with checksum"""
    actual_checksum = calculate_checksum(data)
    return secrets.compare_digest(actual_checksum, expected_checksum)
