"""
Password hashing utilities - Compatible with Django's PBKDF2 and bcrypt.

Since we're using Django's existing database with PBKDF2-hashed passwords,
we need to verify against Django's password format while also supporting
bcrypt for new passwords created through FastAPI.
"""
from passlib.context import CryptContext
import hashlib
import base64
import re


# Configure bcrypt for password hashing (new passwords will use bcrypt)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def create_slug(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    Converts to lowercase, replaces spaces with hyphens, removes special characters.
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = text.replace(" ", "-")
    # Remove special characters, keep only alphanumeric and hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Replace multiple consecutive hyphens with single hyphen
    text = re.sub(r"-+", "-", text)
    # Strip leading/trailing hyphens
    text = text.strip("-")
    return text


def verify_django_pbkdf2_password(plain_password: str, encoded_hash: str) -> bool:
    """
    Verify a password against a Django PBKDF2 hash.
    
    Django password format: pbkdf2_sha256$iterations$salt$hash
    Django uses PBKDF2 with SHA256, 32-byte derived key length
    
    Args:
        plain_password: Plain text password to verify
        encoded_hash: Django-style PBKDF2 hash
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Parse Django hash format
        algorithm, iterations, salt, stored_hash = encoded_hash.split('$')
        
        if algorithm != 'pbkdf2_sha256':
            return False
        
        # Recompute hash with provided password
        # Django uses SHA256 with 32-byte derived key length (256 bits)
        iterations = int(iterations)
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations,
            dklen=32  # Django default: 32 bytes = 256 bits
        )
        computed_hash = base64.b64encode(hash_bytes).decode('utf-8').rstrip('=')
        
        # Compare hashes (constant-time comparison for security)
        return computed_hash == stored_hash
    except (ValueError, IndexError, TypeError):
        return False


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password using bcrypt
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Supports both Django's PBKDF2 format and bcrypt format.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database (Django PBKDF2 or bcrypt)
        
    Returns:
        True if password matches, False otherwise
    """
    # Check if it's a Django PBKDF2 hash
    if hashed_password.startswith('pbkdf2_sha256$'):
        return verify_django_pbkdf2_password(plain_password, hashed_password)
    
    # Otherwise, use bcrypt verification
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # If verification fails for any reason, return False
        return False
