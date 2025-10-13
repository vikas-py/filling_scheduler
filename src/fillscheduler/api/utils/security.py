"""
Security utilities for authentication.

Provides functions for:
- Password hashing and verification (bcrypt)
- JWT token creation and validation
"""

import hashlib
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from fillscheduler.api.config import settings

# Password hashing context
# Using bcrypt with truncate error enabled to handle passwords > 72 bytes
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    For passwords longer than 72 bytes, uses SHA256 pre-hashing to match
    the hashing behavior.

    Args:
        plain_password: Plain text password from user
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    # Apply the same pre-hashing if password is longer than 72 bytes
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    For passwords longer than 72 bytes, uses SHA256 pre-hashing to ensure
    compatibility with bcrypt's byte limit.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # bcrypt has a 72-byte limit. For longer passwords, pre-hash with SHA256
    if len(password.encode("utf-8")) > 72:
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    hashed: str = pwd_context.hash(password)
    return hashed


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of data to encode in token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
