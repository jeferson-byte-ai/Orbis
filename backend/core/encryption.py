"""
End-to-End Encryption Service
Implements AES-256-GCM encryption for audio streams and sensitive data
"""
import os
import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from backend.config import settings


class EncryptionService:
    """Enterprise-grade encryption service"""
    
    def __init__(self):
        """Initialize encryption service with master key"""
        # Derive key from master secret
        self.master_key = self._derive_master_key()
    
    def _derive_master_key(self) -> bytes:
        """Derive master key from settings secret"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=b'orbis_master_salt_v1',  # In production, use random salt stored securely
            iterations=100000,
        )
        return kdf.derive(settings.secret_key.encode())
    
    def generate_room_key(self) -> Tuple[bytes, str]:
        """
        Generate a new room encryption key
        Returns: (key_bytes, key_base64)
        """
        key = AESGCM.generate_key(bit_length=256)
        key_b64 = base64.b64encode(key).decode('utf-8')
        return key, key_b64
    
    def encrypt_audio_chunk(
        self,
        audio_data: bytes,
        room_key: bytes,
        nonce: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt audio chunk with AES-256-GCM
        
        Args:
            audio_data: Raw audio bytes
            room_key: Room's encryption key
            nonce: Optional nonce (generated if not provided)
        
        Returns:
            (encrypted_data, nonce)
        """
        if nonce is None:
            nonce = os.urandom(12)  # 96-bit nonce for GCM
        
        aesgcm = AESGCM(room_key)
        encrypted = aesgcm.encrypt(nonce, audio_data, None)
        
        return encrypted, nonce
    
    def decrypt_audio_chunk(
        self,
        encrypted_data: bytes,
        room_key: bytes,
        nonce: bytes
    ) -> bytes:
        """
        Decrypt audio chunk
        
        Args:
            encrypted_data: Encrypted audio bytes
            room_key: Room's encryption key
            nonce: Nonce used in encryption
        
        Returns:
            Decrypted audio bytes
        """
        aesgcm = AESGCM(room_key)
        return aesgcm.decrypt(nonce, encrypted_data, None)
    
    def encrypt_string(self, data: str) -> Tuple[str, str]:
        """
        Encrypt string data
        Returns: (encrypted_b64, nonce_b64)
        """
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.master_key)
        encrypted = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
        
        return (
            base64.b64encode(encrypted).decode('utf-8'),
            base64.b64encode(nonce).decode('utf-8')
        )
    
    def decrypt_string(self, encrypted_b64: str, nonce_b64: str) -> str:
        """Decrypt string data"""
        encrypted = base64.b64decode(encrypted_b64)
        nonce = base64.b64decode(nonce_b64)
        
        aesgcm = AESGCM(self.master_key)
        decrypted = aesgcm.decrypt(nonce, encrypted, None)
        
        return decrypted.decode('utf-8')
    
    def encrypt_sensitive_data(self, data: dict) -> str:
        """
        Encrypt sensitive data (e.g., OAuth tokens, API keys)
        Returns base64-encoded encrypted data with embedded nonce
        """
        import json
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.master_key)
        
        json_data = json.dumps(data).encode('utf-8')
        encrypted = aesgcm.encrypt(nonce, json_data, None)
        
        # Combine nonce + encrypted for storage
        combined = nonce + encrypted
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt_sensitive_data(self, encrypted_b64: str) -> dict:
        """Decrypt sensitive data"""
        import json
        combined = base64.b64decode(encrypted_b64)
        
        # Extract nonce and encrypted data
        nonce = combined[:12]
        encrypted = combined[12:]
        
        aesgcm = AESGCM(self.master_key)
        decrypted = aesgcm.decrypt(nonce, encrypted, None)
        
        return json.loads(decrypted.decode('utf-8'))
    
    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """
        Hash data with SHA-256
        Useful for generating deterministic IDs
        """
        import hashlib
        if salt:
            data = f"{data}{salt}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


# Global encryption service instance
encryption_service = EncryptionService()
