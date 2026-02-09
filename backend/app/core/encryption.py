"""
Simple encryption utilities for storing sensitive credentials
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings


def _get_fernet_key() -> bytes:
    """
    Derive a Fernet-compatible key from the SECRET_KEY.
    Fernet requires a 32-byte base64-encoded key.
    """
    # Use SHA256 to get a consistent 32-byte key from SECRET_KEY
    key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value.

    Args:
        value: Plain text to encrypt

    Returns:
        Base64-encoded encrypted string
    """
    if not value:
        return ""

    fernet = Fernet(_get_fernet_key())
    encrypted = fernet.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt an encrypted string value.

    Args:
        encrypted_value: Base64-encoded encrypted string

    Returns:
        Decrypted plain text
    """
    if not encrypted_value:
        return ""

    try:
        fernet = Fernet(_get_fernet_key())
        decrypted = fernet.decrypt(encrypted_value.encode())
        return decrypted.decode()
    except Exception:
        # Return empty string if decryption fails
        return ""
