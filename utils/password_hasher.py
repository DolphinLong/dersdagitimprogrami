# -*- coding: utf-8 -*-
"""
Password Hashing Utilities
Provides secure password hashing using bcrypt or fallback to PBKDF2
"""

import binascii
import hashlib
import logging
import secrets

logger = logging.getLogger(__name__)

# Try to import bcrypt (recommended)
try:
    import bcrypt

    BCRYPT_AVAILABLE = True
    logger.info("bcrypt available - using bcrypt for password hashing")
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available - falling back to PBKDF2-HMAC-SHA256")


class PasswordHasher:
    """
    Secure password hashing utility
    
    Uses bcrypt if available, otherwise falls back to PBKDF2-HMAC-SHA256
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password securely
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        if BCRYPT_AVAILABLE:
            return PasswordHasher._hash_bcrypt(password)
        else:
            return PasswordHasher._hash_pbkdf2(password)

    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        """
        Verify a password against a stored hash
        
        Args:
            stored_hash: The stored password hash
            provided_password: The password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        # Detect hash type
        if stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"):
            # bcrypt hash
            return PasswordHasher._verify_bcrypt(stored_hash, provided_password)
        elif stored_hash.startswith("pbkdf2_sha256$"):
            # PBKDF2 hash
            return PasswordHasher._verify_pbkdf2(stored_hash, provided_password)
        else:
            logger.error(f"Unknown hash format: {stored_hash[:20]}...")
            return False

    # ==================== bcrypt methods ====================

    @staticmethod
    def _hash_bcrypt(password: str, rounds: int = 12) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            rounds: Cost factor (default: 12, recommended: 10-14)
            
        Returns:
            bcrypt hash string
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def _verify_bcrypt(stored_hash: str, provided_password: str) -> bool:
        """
        Verify password against bcrypt hash
        
        Args:
            stored_hash: bcrypt hash
            provided_password: Password to verify
            
        Returns:
            True if match, False otherwise
        """
        try:
            password_bytes = provided_password.encode("utf-8")
            stored_bytes = stored_hash.encode("utf-8")
            return bcrypt.checkpw(password_bytes, stored_bytes)
        except Exception as e:
            logger.error(f"bcrypt verification error: {e}")
            return False

    # ==================== PBKDF2 methods (fallback) ====================

    @staticmethod
    def _hash_pbkdf2(password: str, iterations: int = 100_000) -> str:
        """
        Hash password using PBKDF2-HMAC-SHA256
        
        Args:
            password: Plain text password
            iterations: Number of iterations (default: 100,000)
            
        Returns:
            Hash string in format: pbkdf2_sha256$iterations$salt$hash
        """
        salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        salt_hex = binascii.hexlify(salt).decode()
        hash_hex = binascii.hexlify(dk).decode()
        return f"pbkdf2_sha256${iterations}${salt_hex}${hash_hex}"

    @staticmethod
    def _verify_pbkdf2(stored_hash: str, provided_password: str) -> bool:
        """
        Verify password against PBKDF2 hash
        
        Args:
            stored_hash: PBKDF2 hash
            provided_password: Password to verify
            
        Returns:
            True if match, False otherwise
        """
        try:
            parts = stored_hash.split("$")
            if len(parts) != 4:
                return False

            _, iter_str, salt_hex, hash_hex = parts
            iterations = int(iter_str)
            salt = binascii.unhexlify(salt_hex)
            expected = binascii.unhexlify(hash_hex)

            dk = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, iterations)
            return secrets.compare_digest(dk, expected)
        except Exception as e:
            logger.error(f"PBKDF2 verification error: {e}")
            return False


# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password (convenience function)"""
    return PasswordHasher.hash_password(password)


def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verify a password (convenience function)"""
    return PasswordHasher.verify_password(stored_hash, provided_password)
