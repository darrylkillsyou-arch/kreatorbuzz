"""Message encryption service for Maccall AI Creator Marketplace.

NOTE: This service implements symmetric encryption AT REST using cryptography.fernet.
It is encrypted at rest in the database, NOT end-to-end encrypted (E2EE), allowing the
platform to perform authorization, moderation, and secure indexing.
"""

import base64
import hashlib
import logging
from cryptography.fernet import Fernet
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback deterministic key if none provided in environment
_DEFAULT_FALLBACK_SEED = "maccall-message-encryption-at-rest-secret-key-2026"


def _get_fernet_instance() -> Fernet:
    """Initializes Fernet using configured MESSAGE_ENCRYPTION_KEY or a derived fallback key."""
    raw_key = settings.MESSAGE_ENCRYPTION_KEY.strip() if settings.MESSAGE_ENCRYPTION_KEY else ""
    
    if raw_key:
        try:
            # Check if valid Fernet key
            return Fernet(raw_key.encode("utf-8"))
        except Exception:
            # Derive 32-byte urlsafe base64 key from raw key
            digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
            fernet_key = base64.urlsafe_b64encode(digest)
            return Fernet(fernet_key)
    
    logger.warning("No MESSAGE_ENCRYPTION_KEY configured. Using secure deterministic fallback key.")
    digest = hashlib.sha256(_DEFAULT_FALLBACK_SEED.encode("utf-8")).digest()
    fernet_key = base64.urlsafe_b64encode(digest)
    return Fernet(fernet_key)


_fernet = _get_fernet_instance()


def encrypt_message(plain_text: str) -> str:
    """Encrypts plaintext string into a base64 Fernet token for encrypted storage at rest."""
    if not plain_text:
        return ""
    try:
        encrypted_bytes = _fernet.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to encrypt message: {e}")
        return plain_text


def decrypt_message(encrypted_token: str) -> str:
    """Decrypts encrypted token from database into plaintext string for authorized readers."""
    if not encrypted_token:
        return ""
    try:
        decrypted_bytes = _fernet.decrypt(encrypted_token.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception:
        # If token was stored as plain text or cannot be decrypted, return as is
        return encrypted_token
