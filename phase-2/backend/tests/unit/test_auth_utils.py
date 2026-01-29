"""Unit tests for password hashing utilities.

T034: [US1] Unit test for password hashing
Tests bcrypt hash generation and verification.
"""

import os

# Set environment variables BEFORE importing from src.utils.auth
# This ensures JWT_SECRET and JWT_ALGORITHM are available when the module loads
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

import pytest


class TestPasswordHashing:
    """Tests for hash_password and verify_password functions."""

    def test_hash_password_returns_bcrypt_hash(self):
        """Test that hash_password returns a valid bcrypt hash."""
        from src.utils.auth import hash_password

        password = "SecurePass123!"
        hashed = hash_password(password)

        # Bcrypt hashes start with $2b$ and are 60 characters
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

    def test_hash_password_uses_minimum_12_rounds(self):
        """Test that hash_password uses at least 12 rounds for security."""
        from src.utils.auth import hash_password

        password = "SecurePass123!"
        hashed = hash_password(password)

        # Extract rounds from hash (format: $2b$XX$...)
        rounds = int(hashed.split("$")[2])
        assert rounds >= 12, "Bcrypt should use at least 12 rounds for security"

    def test_hash_password_produces_unique_hashes(self):
        """Test that same password produces different hashes (unique salt)."""
        from src.utils.auth import hash_password

        password = "SecurePass123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Same password should produce different hashes due to random salt
        assert hash1 != hash2, "Each hash should have unique salt"

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        from src.utils.auth import hash_password, verify_password

        password = "SecurePass123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        from src.utils.auth import hash_password, verify_password

        password = "SecurePass123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """Test that verify_password handles empty password correctly."""
        from src.utils.auth import hash_password, verify_password

        password = "SecurePass123!"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_verify_password_invalid_hash_format(self):
        """Test that verify_password returns False for invalid hash format."""
        from src.utils.auth import verify_password

        password = "SecurePass123!"
        invalid_hash = "not_a_valid_bcrypt_hash"

        # Should return False, not raise exception
        assert verify_password(password, invalid_hash) is False

    def test_verify_password_empty_hash(self):
        """Test that verify_password handles empty hash correctly."""
        from src.utils.auth import verify_password

        password = "SecurePass123!"

        assert verify_password(password, "") is False


class TestTokenCreation:
    """Tests for JWT token creation functions."""

    def test_create_access_token_contains_required_claims(self):
        """Test that access token contains all required claims."""
        from uuid import uuid4
        import jwt

        from src.utils.auth import create_access_token, JWT_SECRET, JWT_ALGORITHM

        user_id = uuid4()
        email = "test@example.com"

        token = create_access_token(user_id, email)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert payload["token_type"] == "access"
        assert "iat" in payload
        assert "exp" in payload

    def test_create_access_token_expires_in_1_hour(self):
        """Test that access token expires in approximately 1 hour."""
        from uuid import uuid4
        import jwt

        from src.utils.auth import create_access_token, JWT_SECRET, JWT_ALGORITHM

        user_id = uuid4()
        email = "test@example.com"

        token = create_access_token(user_id, email)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})

        # Expiration should be approximately 1 hour (3600 seconds) from now
        exp_delta = payload["exp"] - payload["iat"]
        assert 3590 <= exp_delta <= 3610  # Allow 10 second tolerance

    def test_create_refresh_token_contains_required_claims(self):
        """Test that refresh token contains all required claims."""
        from uuid import uuid4
        import jwt

        from src.utils.auth import create_refresh_token, JWT_SECRET, JWT_ALGORITHM

        user_id = uuid4()
        email = "test@example.com"

        token = create_refresh_token(user_id, email)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert payload["token_type"] == "refresh"

    def test_create_refresh_token_expires_in_7_days(self):
        """Test that refresh token expires in approximately 7 days."""
        from uuid import uuid4
        import jwt

        from src.utils.auth import create_refresh_token, JWT_SECRET, JWT_ALGORITHM

        user_id = uuid4()
        email = "test@example.com"

        token = create_refresh_token(user_id, email)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Expiration should be approximately 7 days (604800 seconds) from now
        exp_delta = payload["exp"] - payload["iat"]
        expected_seconds = 7 * 24 * 60 * 60  # 7 days in seconds
        assert expected_seconds - 10 <= exp_delta <= expected_seconds + 10

    def test_create_password_reset_token_expires_in_1_hour(self):
        """Test that password reset token expires in 1 hour."""
        from uuid import uuid4
        import jwt

        from src.utils.auth import create_password_reset_token, JWT_SECRET, JWT_ALGORITHM

        user_id = uuid4()
        email = "test@example.com"

        token = create_password_reset_token(user_id, email)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})

        assert payload["token_type"] == "password_reset"
        exp_delta = payload["exp"] - payload["iat"]
        assert 3590 <= exp_delta <= 3610  # 1 hour with tolerance

    def test_create_email_verification_token_expires_in_24_hours(self):
        """Test that email verification token expires in 24 hours."""
        from uuid import uuid4
        import jwt

        from src.utils.auth import create_email_verification_token, JWT_SECRET, JWT_ALGORITHM

        user_id = uuid4()
        email = "test@example.com"

        token = create_email_verification_token(user_id, email)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        assert payload["token_type"] == "email_verification"
        exp_delta = payload["exp"] - payload["iat"]
        expected_seconds = 24 * 60 * 60  # 24 hours
        assert expected_seconds - 10 <= exp_delta <= expected_seconds + 10
