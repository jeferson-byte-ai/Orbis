"""
Enhanced Security Features - BigTech Level
Implements 2FA, API key hashing, password breach check, etc.
"""
import secrets
import hashlib
import base64
import json
from typing import Optional, Tuple, List
from datetime import datetime, timedelta
import pyotp
import qrcode
from io import BytesIO
import httpx
from sqlalchemy.orm import Session

from backend.core.encryption import encryption_service
from backend.core.security import get_password_hash, verify_password
from backend.config import settings


class TwoFactorAuthService:
    """Two-Factor Authentication service using TOTP"""
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    def get_totp_uri(self, secret: str, email: str) -> str:
        """
        Generate TOTP URI for QR code
        
        Args:
            secret: TOTP secret
            email: User's email
        
        Returns:
            otpauth:// URI
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="Orbis"
        )
    
    def generate_qr_code(self, secret: str, email: str) -> bytes:
        """
        Generate QR code image for TOTP setup
        
        Returns:
            PNG image bytes
        """
        uri = self.get_totp_uri(secret, email)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def verify_code(self, secret: str, code: str) -> bool:
        """
        Verify TOTP code
        
        Args:
            secret: TOTP secret
            code: 6-digit code from authenticator app
        
        Returns:
            True if valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        # Allow 1 time step before/after for clock skew
        return totp.verify(code, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for 2FA recovery
        
        Returns:
            List of backup codes (plain text)
        """
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice('0123456789') for _ in range(8))
            # Format: XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes
    
    def hash_backup_codes(self, codes: List[str]) -> str:
        """
        Hash backup codes for storage
        
        Returns:
            JSON string of hashed codes
        """
        hashed = [hashlib.sha256(code.encode()).hexdigest() for code in codes]
        return json.dumps(hashed)
    
    def verify_backup_code(self, code: str, hashed_codes_json: str) -> bool:
        """
        Verify a backup code
        
        Returns:
            True if valid (and removes it from list)
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        hashed_codes = json.loads(hashed_codes_json)
        
        if code_hash in hashed_codes:
            hashed_codes.remove(code_hash)
            return True, json.dumps(hashed_codes)
        
        return False, hashed_codes_json


class APIKeyService:
    """Secure API Key management with hashing"""
    
    def generate_api_key(self) -> Tuple[str, str, str]:
        """
        Generate a new API key
        
        Returns:
            (full_key, key_hash, key_prefix)
        """
        # Generate random key
        random_bytes = secrets.token_bytes(32)
        key = f"sk_live_{base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')}"
        
        # Hash for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        # Prefix for identification
        key_prefix = key[:15]  # "sk_live_XXXXXXX"
        
        return key, key_hash, key_prefix
    
    def hash_api_key(self, key: str) -> str:
        """Hash an API key for verification"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def verify_api_key(self, provided_key: str, stored_hash: str) -> bool:
        """Verify API key against stored hash"""
        provided_hash = self.hash_api_key(provided_key)
        return secrets.compare_digest(provided_hash, stored_hash)


class PasswordSecurityService:
    """Enhanced password security"""
    
    async def check_password_breach(self, password: str) -> Tuple[bool, int]:
        """
        Check if password has been in a data breach using HaveIBeenPwned API
        
        Returns:
            (is_breached, times_seen)
        """
        try:
            # Hash password with SHA-1
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            # Query HIBP API (k-anonymity model - only sends first 5 chars)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://api.pwnedpasswords.com/range/{prefix}',
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    # API error - assume not breached to not block user
                    return False, 0
                
                # Check if suffix exists in response
                for line in response.text.split('\r\n'):
                    if ':' in line:
                        hash_suffix, count = line.split(':')
                        if hash_suffix == suffix:
                            return True, int(count)
            
            return False, 0
            
        except Exception:
            # On error, don't block user
            return False, 0
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str], int]:
        """
        Enhanced password validation
        
        Returns:
            (is_valid, issues, strength_score)
        """
        issues = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters")
        elif len(password) >= 12:
            score += 2
        elif len(password) >= 10:
            score += 1
        
        # Character variety
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not has_upper:
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        if not has_lower:
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        if not has_digit:
            issues.append("Password must contain at least one number")
        else:
            score += 1
        
        if not has_special:
            issues.append("Password should contain at least one special character")
        else:
            score += 2
        
        # Common patterns check
        common_patterns = ['123456', 'password', 'qwerty', 'abc123', '111111']
        if any(pattern in password.lower() for pattern in common_patterns):
            issues.append("Password contains common patterns")
            score -= 2
        
        # Sequential characters
        if any(password[i:i+3].isdigit() and int(password[i+1]) == int(password[i])+1 and int(password[i+2]) == int(password[i])+2 
               for i in range(len(password)-2) if password[i:i+3].isdigit()):
            score -= 1
        
        score = max(0, min(10, score))  # Clamp between 0-10
        
        return (len(issues) == 0, issues, score)
    
    def check_password_reuse(self, password: str, password_history: List[str]) -> bool:
        """
        Check if password was used before
        
        Args:
            password: New password (plain)
            password_history: List of previous password hashes
        
        Returns:
            True if password was used before
        """
        for old_hash in password_history:
            if verify_password(password, old_hash):
                return True
        return False


class KeyRotationService:
    """Encryption key rotation service"""
    
    def should_rotate_key(self, key_created_at: datetime, rotation_days: int = 90) -> bool:
        """Check if key should be rotated based on age"""
        age_days = (datetime.utcnow() - key_created_at).days
        return age_days >= rotation_days
    
    def rotate_room_key(self, old_key: bytes) -> bytes:
        """Generate new room key for rotation"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM.generate_key(bit_length=256)
    
    async def schedule_key_rotation(
        self,
        db: Session,
        key_type: str,
        key_version: int,
        records_count: int
    ):
        """Schedule a key rotation job"""
        from backend.db.models_security import EncryptionKeyRotation
        
        rotation = EncryptionKeyRotation(
            key_type=key_type,
            key_version=key_version,
            status="pending",
            records_to_rotate=records_count,
            triggered_by="auto"
        )
        
        db.add(rotation)
        db.commit()
        
        return rotation


class SecurityEventLogger:
    """Log security events for monitoring and compliance"""
    
    async def log_event(
        self,
        db: Session,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """Log a security event"""
        from backend.db.models_security import SecurityEvent
        
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        db.add(event)
        db.commit()
        
        # TODO: Send alert if severity is high/critical
        if severity in ['high', 'critical']:
            # Send email/slack notification
            pass
        
        return event
    
    async def log_failed_login(
        self,
        db: Session,
        email: str,
        ip_address: str,
        reason: str
    ):
        """Log failed login attempt"""
        await self.log_event(
            db=db,
            event_type="login_failed",
            severity="medium",
            description=f"Failed login attempt for {email}: {reason}",
            ip_address=ip_address,
            metadata={"email": email, "reason": reason}
        )
    
    async def log_suspicious_activity(
        self,
        db: Session,
        user_id: str,
        activity: str,
        ip_address: str
    ):
        """Log suspicious activity"""
        await self.log_event(
            db=db,
            event_type="suspicious_activity",
            severity="high",
            description=f"Suspicious activity detected: {activity}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={"activity": activity}
        )


# Global instances
two_factor_service = TwoFactorAuthService()
api_key_service = APIKeyService()
password_security_service = PasswordSecurityService()
key_rotation_service = KeyRotationService()
security_event_logger = SecurityEventLogger()
