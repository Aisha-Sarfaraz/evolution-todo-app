"""Integration tests for JWT authentication security.

T079: [US3] Integration test for JWT security
Tests for missing, expired, malformed, and invalid tokens.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
import jwt
import time
import os


JWT_SECRET = os.environ.get("JWT_SECRET", "test-secret-key-for-testing-only-32chars")


def create_test_token(
    user_id: str,
    expired: bool = False,
    wrong_secret: bool = False,
    wrong_type: bool = False,
) -> str:
    """Create a JWT token for testing with various conditions."""
    payload = {
        "sub": user_id,
        "email": f"user_{user_id[:8]}@example.com",
        "iat": int(time.time()),
        "exp": int(time.time()) - 3600 if expired else int(time.time()) + 3600,
        "token_type": "refresh" if wrong_type else "access",
    }
    secret = "wrong-secret-key" if wrong_secret else JWT_SECRET
    return jwt.encode(payload, secret, algorithm="HS256")


class TestJWTSecurityMissingToken:
    """Tests for requests without authentication token."""

    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, async_client: AsyncClient):
        """Test that missing Authorization header returns 401."""
        user_id = str(uuid4())
        response = await async_client.get(f"/api/{user_id}/tasks")

        assert response.status_code == 401
        data = response.json()
        assert data.get("error_code") == "UNAUTHORIZED" or data.get("detail", {}).get("error_code") in ["AUTHENTICATION_REQUIRED", "INVALID_TOKEN", "TOKEN_EXPIRED", "UNAUTHORIZED"]
        detail_msg = data.get("detail", {}).get("detail", str(data.get("detail", ""))).lower()
        assert "token" in detail_msg or "auth" in detail_msg

    @pytest.mark.asyncio
    async def test_empty_authorization_header_returns_401(self, async_client: AsyncClient):
        """Test that empty Authorization header returns 401."""
        user_id = str(uuid4())
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": ""},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_bearer_prefix_returns_401(self, async_client: AsyncClient):
        """Test that Authorization without Bearer prefix returns 401."""
        user_id = str(uuid4())
        token = create_test_token(user_id)
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": token},  # Missing "Bearer " prefix
        )

        assert response.status_code == 401


class TestJWTSecurityExpiredToken:
    """Tests for expired JWT tokens."""

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(self, async_client: AsyncClient):
        """Test that expired token returns 401."""
        user_id = str(uuid4())
        token = create_test_token(user_id, expired=True)
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data.get("error_code") == "UNAUTHORIZED" or data.get("detail", {}).get("error_code") in ["AUTHENTICATION_REQUIRED", "INVALID_TOKEN", "TOKEN_EXPIRED", "UNAUTHORIZED"]
        detail_msg = data.get("detail", {}).get("detail", str(data.get("detail", ""))).lower()
        assert "expired" in detail_msg or "token" in detail_msg

    @pytest.mark.asyncio
    async def test_expired_token_on_post_returns_401(self, async_client: AsyncClient):
        """Test that expired token on POST returns 401."""
        user_id = str(uuid4())
        token = create_test_token(user_id, expired=True)
        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401


class TestJWTSecurityMalformedToken:
    """Tests for malformed JWT tokens."""

    @pytest.mark.asyncio
    async def test_malformed_token_returns_401(self, async_client: AsyncClient):
        """Test that malformed token returns 401."""
        user_id = str(uuid4())
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": "Bearer not-a-valid-jwt-token"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data.get("error_code") == "UNAUTHORIZED" or data.get("detail", {}).get("error_code") in ["AUTHENTICATION_REQUIRED", "INVALID_TOKEN", "TOKEN_EXPIRED", "UNAUTHORIZED"]

    @pytest.mark.asyncio
    async def test_incomplete_jwt_structure_returns_401(self, async_client: AsyncClient):
        """Test that incomplete JWT (missing parts) returns 401."""
        user_id = str(uuid4())
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9"},  # Only header
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_bearer_token_returns_401(self, async_client: AsyncClient):
        """Test that 'Bearer ' with no token returns 401."""
        user_id = str(uuid4())
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": "Bearer "},
        )

        assert response.status_code == 401


class TestJWTSecurityInvalidSignature:
    """Tests for tokens with invalid signatures."""

    @pytest.mark.asyncio
    async def test_wrong_secret_returns_401(self, async_client: AsyncClient):
        """Test that token signed with wrong secret returns 401."""
        user_id = str(uuid4())
        token = create_test_token(user_id, wrong_secret=True)
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data.get("error_code") == "UNAUTHORIZED" or data.get("detail", {}).get("error_code") in ["AUTHENTICATION_REQUIRED", "INVALID_TOKEN", "TOKEN_EXPIRED", "UNAUTHORIZED"]
        detail_msg = data.get("detail", {}).get("detail", str(data.get("detail", ""))).lower()
        assert "invalid" in detail_msg or "signature" in detail_msg or "token" in detail_msg

    @pytest.mark.asyncio
    async def test_tampered_payload_returns_401(self, async_client: AsyncClient):
        """Test that tampered token payload returns 401."""
        user_id = str(uuid4())
        # Create a valid token and tamper with it
        token = create_test_token(user_id)
        parts = token.split(".")
        # Tamper with payload (second part)
        tampered_payload = parts[1] + "tampered"
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {tampered_token}"},
        )

        assert response.status_code == 401


class TestJWTSecurityWrongTokenType:
    """Tests for tokens with wrong type (refresh used as access)."""

    @pytest.mark.asyncio
    async def test_refresh_token_as_access_returns_401(self, async_client: AsyncClient):
        """Test that using refresh token as access token returns 401."""
        user_id = str(uuid4())
        token = create_test_token(user_id, wrong_type=True)
        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data.get("error_code") == "UNAUTHORIZED" or data.get("detail", {}).get("error_code") in ["AUTHENTICATION_REQUIRED", "INVALID_TOKEN", "TOKEN_EXPIRED", "UNAUTHORIZED"]


class TestJWTSecurityMissingClaims:
    """Tests for tokens missing required claims."""

    @pytest.mark.asyncio
    async def test_missing_sub_claim_returns_401(self, async_client: AsyncClient):
        """Test that token without 'sub' claim returns 401."""
        payload = {
            "email": "test@example.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "token_type": "access",
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        user_id = str(uuid4())

        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_exp_claim_returns_401(self, async_client: AsyncClient):
        """Test that token without 'exp' claim returns 401."""
        user_id = str(uuid4())
        payload = {
            "sub": user_id,
            "email": "test@example.com",
            "iat": int(time.time()),
            "token_type": "access",
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

        response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

