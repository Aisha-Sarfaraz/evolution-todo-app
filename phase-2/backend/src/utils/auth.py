"""Authentication utilities for password hashing and verification.

T025: Password hashing utilities
T084: Account lockout logic (5 failed attempts = 15 minute lockout)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID
from threading import Lock
import os
import time

import bcrypt
import jwt


# JWT configuration from environment
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # 7 days

# Bcrypt configuration (minimum 10 rounds for security)
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with secure work factor.

    Uses bcrypt with 12 rounds (2^12 iterations) which provides
    strong protection against brute-force attacks while maintaining
    acceptable performance (~250ms per hash).

    Args:
        password: Plain text password to hash

    Returns:
        str: Bcrypt hash string (60 characters, includes salt)

    Security Notes:
        - Bcrypt automatically generates a random salt
        - 12 rounds provides ~4096x more work than 1 round
        - Hash output is fixed-length regardless of input
        - Timing-safe comparison used in verify_password

    Example:
        >>> hash_password("SecurePass123!")
        '$2b$12$K4...'  # 60-char bcrypt hash
    """
    # Encode password to bytes and generate salt
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)

    # Hash password with salt
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.
    The hash contains the salt, so no separate salt storage needed.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash from database

    Returns:
        bool: True if password matches, False otherwise

    Security Notes:
        - Constant-time comparison prevents timing attacks
        - Salt is extracted from hash automatically
        - Returns False for any invalid hash format

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")

        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, TypeError):
        # Invalid hash format
        return False


def create_access_token(
    user_id: UUID,
    email: str,
    expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token for authentication.

    Args:
        user_id: User's UUID identifier
        email: User's email address
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT access token

    Token Claims:
        - sub: User ID (string UUID)
        - email: User email
        - iat: Issued at timestamp
        - exp: Expiration timestamp (1 hour default)
        - token_type: "access"
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.utcnow()
    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "token_type": "access"
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    email: str,
    expires_delta: timedelta | None = None
) -> str:
    """Create a JWT refresh token for session renewal.

    Args:
        user_id: User's UUID identifier
        email: User's email address
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT refresh token

    Token Claims:
        - sub: User ID (string UUID)
        - email: User email
        - iat: Issued at timestamp
        - exp: Expiration timestamp (7 days default)
        - token_type: "refresh"
    """
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    now = datetime.utcnow()
    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "token_type": "refresh"
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_password_reset_token(
    user_id: UUID,
    email: str
) -> str:
    """Create a password reset token with 1-hour expiration.

    Args:
        user_id: User's UUID identifier
        email: User's email address

    Returns:
        str: Encoded JWT reset token

    Token Claims:
        - sub: User ID (string UUID)
        - email: User email
        - iat: Issued at timestamp
        - exp: Expiration timestamp (1 hour)
        - token_type: "password_reset"
    """
    now = datetime.utcnow()
    expire = now + timedelta(hours=1)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "token_type": "password_reset"
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_email_verification_token(
    user_id: UUID,
    email: str
) -> str:
    """Create an email verification token with 24-hour expiration.

    Args:
        user_id: User's UUID identifier
        email: User's email address

    Returns:
        str: Encoded JWT verification token

    Token Claims:
        - sub: User ID (string UUID)
        - email: User email
        - iat: Issued at timestamp
        - exp: Expiration timestamp (24 hours)
        - token_type: "email_verification"
    """
    now = datetime.utcnow()
    expire = now + timedelta(hours=24)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "token_type": "email_verification"
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ============================================================================
# Account Lockout Logic (T084)
# ============================================================================

# Account lockout configuration
MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))


@dataclass
class FailedAttemptEntry:
    """Track failed signin attempts for an account."""

    attempts: int = 0
    first_attempt_time: float = 0.0
    locked_until: Optional[float] = None


class AccountLockoutStore:
    """Thread-safe in-memory store for tracking failed signin attempts."""

    def __init__(
        self,
        max_attempts: int = MAX_FAILED_ATTEMPTS,
        lockout_minutes: int = LOCKOUT_DURATION_MINUTES,
    ):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_minutes * 60
        self._store: dict[str, FailedAttemptEntry] = {}
        self._lock = Lock()

    def check_lockout(self, email: str) -> tuple[bool, int]:
        """
        Check if an account is currently locked out.

        Args:
            email: Email address to check

        Returns:
            tuple of (is_locked, seconds_remaining)
        """
        email_lower = email.lower()
        current_time = time.time()

        with self._lock:
            entry = self._store.get(email_lower)
            if not entry:
                return (False, 0)

            # Check if locked
            if entry.locked_until and current_time < entry.locked_until:
                remaining = int(entry.locked_until - current_time)
                return (True, max(1, remaining))

            # Check if lockout expired
            if entry.locked_until and current_time >= entry.locked_until:
                # Reset after lockout expires
                del self._store[email_lower]
                return (False, 0)

            return (False, 0)

    def record_failed_attempt(self, email: str) -> tuple[bool, int, int]:
        """
        Record a failed signin attempt.

        Args:
            email: Email address that failed signin

        Returns:
            tuple of (is_now_locked, seconds_locked_for, attempts_remaining)
        """
        email_lower = email.lower()
        current_time = time.time()

        with self._lock:
            entry = self._store.get(email_lower)

            if not entry:
                # First failed attempt
                self._store[email_lower] = FailedAttemptEntry(
                    attempts=1,
                    first_attempt_time=current_time,
                )
                return (False, 0, self.max_attempts - 1)

            # Check if already locked
            if entry.locked_until and current_time < entry.locked_until:
                remaining = int(entry.locked_until - current_time)
                return (True, remaining, 0)

            # Check if lockout expired - reset
            if entry.locked_until and current_time >= entry.locked_until:
                self._store[email_lower] = FailedAttemptEntry(
                    attempts=1,
                    first_attempt_time=current_time,
                )
                return (False, 0, self.max_attempts - 1)

            # Increment attempts
            entry.attempts += 1

            # Check if should lock
            if entry.attempts >= self.max_attempts:
                entry.locked_until = current_time + self.lockout_seconds
                return (True, self.lockout_seconds, 0)

            return (False, 0, self.max_attempts - entry.attempts)

    def record_successful_signin(self, email: str) -> None:
        """
        Clear failed attempts after successful signin.

        Args:
            email: Email address that successfully signed in
        """
        email_lower = email.lower()

        with self._lock:
            if email_lower in self._store:
                del self._store[email_lower]

    def get_attempts(self, email: str) -> int:
        """Get current number of failed attempts for an email."""
        email_lower = email.lower()

        with self._lock:
            entry = self._store.get(email_lower)
            return entry.attempts if entry else 0

    def reset(self, email: str) -> None:
        """Manually reset lockout for an email (admin action)."""
        email_lower = email.lower()

        with self._lock:
            if email_lower in self._store:
                del self._store[email_lower]


# Global lockout store instance
_lockout_store: Optional[AccountLockoutStore] = None


def get_lockout_store() -> AccountLockoutStore:
    """Get or create the account lockout store singleton."""
    global _lockout_store
    if _lockout_store is None:
        _lockout_store = AccountLockoutStore()
    return _lockout_store


def check_account_lockout(email: str) -> tuple[bool, int]:
    """
    Check if an account is locked out.

    Args:
        email: Email to check

    Returns:
        tuple of (is_locked, minutes_remaining)
    """
    store = get_lockout_store()
    is_locked, seconds = store.check_lockout(email)
    minutes = (seconds + 59) // 60  # Round up to nearest minute
    return (is_locked, minutes)


def record_failed_signin(email: str) -> tuple[bool, int]:
    """
    Record a failed signin attempt and check if account should be locked.

    Args:
        email: Email that failed signin

    Returns:
        tuple of (is_now_locked, minutes_locked_for)
    """
    store = get_lockout_store()
    is_locked, seconds, _ = store.record_failed_attempt(email)
    minutes = (seconds + 59) // 60 if seconds > 0 else LOCKOUT_DURATION_MINUTES
    return (is_locked, minutes)


def record_successful_signin(email: str) -> None:
    """
    Clear failed attempts after successful signin.

    Args:
        email: Email that successfully signed in
    """
    store = get_lockout_store()
    store.record_successful_signin(email)
