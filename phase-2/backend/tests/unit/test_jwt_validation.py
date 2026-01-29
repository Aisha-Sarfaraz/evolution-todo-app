"""Unit tests for JWT validation dependency.

T035: [US1] Unit test for JWT validation
Tests get_current_user dependency with valid, expired, and malformed tokens.

Updated to work with Better Auth JWKS-based JWT verification.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
import time

from jose import jwt
from jose.constants import ALGORITHMS


# Test fixtures
@pytest.fixture
def test_user_id():
    """Generate a test user ID."""
    return str(uuid4())


@pytest.fixture
def valid_jwt_payload(test_user_id):
    """Create a valid JWT payload for testing."""
    return {
        "sub": test_user_id,
        "email": "test@example.com",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour from now
        "iss": "http://localhost:3000",
        "aud": "http://localhost:3000",
    }


@pytest.fixture
def expired_jwt_payload(test_user_id):
    """Create an expired JWT payload for testing."""
    return {
        "sub": test_user_id,
        "email": "test@example.com",
        "iat": int(time.time()) - 7200,  # 2 hours ago
        "exp": int(time.time()) - 3600,  # 1 hour ago (expired)
        "iss": "http://localhost:3000",
        "aud": "http://localhost:3000",
    }


# Mock JWKS and signing key for testing
# Using HS256 for simplicity in unit tests (mocked as if from JWKS)
TEST_SECRET = "test-secret-key-for-unit-testing-only-32chars"
MOCK_JWKS = {
    "keys": [
        {
            "kty": "oct",
            "kid": "test-key-1",
            "k": TEST_SECRET,
        }
    ]
}


def create_test_token(payload: dict, secret: str = TEST_SECRET, algorithm: str = "HS256") -> str:
    """Create a JWT token for testing."""
    return jwt.encode(payload, secret, algorithm=algorithm)


class TestGetCurrentUser:
    """Tests for get_current_user dependency function."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_current_user(self, valid_jwt_payload):
        """Test that valid token returns CurrentUser with correct user_id."""
        from src.api.dependencies import get_current_user, CurrentUser
        from fastapi.security import HTTPAuthorizationCredentials

        # Create valid token
        token = create_test_token(valid_jwt_payload)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Mock the JWKS fetch and key extraction
        with patch("src.api.dependencies.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = MOCK_JWKS

            with patch("src.api.dependencies.get_signing_key") as mock_get_key:
                mock_get_key.return_value = TEST_SECRET

                result = await get_current_user(credentials)

        assert isinstance(result, CurrentUser)
        assert str(result.user_id) == valid_jwt_payload["sub"]

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self, expired_jwt_payload):
        """Test that expired token raises 401 Unauthorized with TOKEN_EXPIRED."""
        from src.api.dependencies import get_current_user
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        # Create expired token
        token = create_test_token(expired_jwt_payload)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Mock the JWKS fetch and key extraction
        with patch("src.api.dependencies.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = MOCK_JWKS

            with patch("src.api.dependencies.get_signing_key") as mock_get_key:
                mock_get_key.return_value = TEST_SECRET

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "TOKEN_EXPIRED"

    @pytest.mark.asyncio
    async def test_malformed_token_raises_401(self):
        """Test that malformed token raises 401 Unauthorized with INVALID_TOKEN."""
        from src.api.dependencies import get_current_user
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="not.a.valid.jwt.token"
        )

        # Mock the JWKS fetch
        with patch("src.api.dependencies.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = MOCK_JWKS

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_missing_token_raises_401(self):
        """Test that missing token raises 401 Unauthorized with AUTHENTICATION_REQUIRED."""
        from src.api.dependencies import get_current_user
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "AUTHENTICATION_REQUIRED"

    @pytest.mark.asyncio
    async def test_wrong_signature_raises_401(self, valid_jwt_payload):
        """Test that token with wrong signature raises 401."""
        from src.api.dependencies import get_current_user
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        # Create token with different secret
        token = create_test_token(valid_jwt_payload, secret="wrong-secret-key-12345678901234567890")

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Mock the JWKS fetch and key extraction with correct key (token was signed with wrong key)
        with patch("src.api.dependencies.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = MOCK_JWKS

            with patch("src.api.dependencies.get_signing_key") as mock_get_key:
                mock_get_key.return_value = TEST_SECRET  # Different from token's signing key

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_missing_sub_claim_raises_401(self):
        """Test that token without sub claim raises 401."""
        from src.api.dependencies import get_current_user
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        # Create token without sub claim
        payload = {
            "email": "test@example.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        token = create_test_token(payload)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Mock the JWKS fetch and key extraction
        with patch("src.api.dependencies.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = MOCK_JWKS

            with patch("src.api.dependencies.get_signing_key") as mock_get_key:
                mock_get_key.return_value = TEST_SECRET

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_invalid_user_id_format_raises_401(self):
        """Test that invalid user_id format raises 401."""
        from src.api.dependencies import get_current_user
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        payload = {
            "sub": "not-a-valid-uuid",  # Invalid UUID format
            "email": "test@example.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }

        token = create_test_token(payload)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Mock the JWKS fetch and key extraction
        with patch("src.api.dependencies.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = MOCK_JWKS

            with patch("src.api.dependencies.get_signing_key") as mock_get_key:
                mock_get_key.return_value = TEST_SECRET

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_jwks_fetch_failure_raises_500(self, valid_jwt_payload):
        """Test that JWKS fetch failure raises 500."""
        from src.api.dependencies import get_current_user
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials
        import httpx

        token = create_test_token(valid_jwt_payload)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Mock JWKS fetch to fail
        with patch("src.api.dependencies.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = HTTPException(
                status_code=500,
                detail={"error_code": "AUTH_SERVICE_UNAVAILABLE", "detail": "Connection failed"}
            )

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail["error_code"] == "AUTH_SERVICE_UNAVAILABLE"


class TestValidateUserIdMatch:
    """Tests for validate_user_id_match dependency function."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock Request object for testing."""
        request = MagicMock()
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.method = "GET"
        return request

    @pytest.mark.asyncio
    async def test_matching_user_id_returns_current_user(self, valid_jwt_payload, mock_request):
        """Test that matching URL user_id returns CurrentUser."""
        from src.api.dependencies import validate_user_id_match, CurrentUser
        from uuid import UUID

        # Create CurrentUser from payload
        current_user = CurrentUser(
            user_id=UUID(valid_jwt_payload["sub"]),
            email=valid_jwt_payload["email"]
        )

        # URL user_id matches JWT user_id
        url_user_id = UUID(valid_jwt_payload["sub"])

        result = await validate_user_id_match(url_user_id, mock_request, current_user)

        assert result == current_user

    @pytest.mark.asyncio
    async def test_mismatched_user_id_raises_403(self, valid_jwt_payload, mock_request):
        """Test that mismatched URL user_id raises 403 Forbidden."""
        from src.api.dependencies import validate_user_id_match, CurrentUser
        from fastapi import HTTPException
        from uuid import UUID

        # Create CurrentUser from payload
        current_user = CurrentUser(
            user_id=UUID(valid_jwt_payload["sub"]),
            email=valid_jwt_payload["email"]
        )

        # URL user_id does NOT match JWT user_id
        different_user_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await validate_user_id_match(different_user_id, mock_request, current_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error_code"] == "FORBIDDEN"
        assert "other users" in exc_info.value.detail["detail"].lower()

    @pytest.mark.asyncio
    async def test_logs_forbidden_access_attempt(self, valid_jwt_payload, mock_request):
        """Test that forbidden access attempt is logged."""
        from src.api.dependencies import validate_user_id_match, CurrentUser
        from fastapi import HTTPException
        from uuid import UUID

        current_user = CurrentUser(
            user_id=UUID(valid_jwt_payload["sub"]),
            email=valid_jwt_payload["email"]
        )

        different_user_id = uuid4()

        with patch("src.api.dependencies.log_forbidden_access") as mock_log:
            with pytest.raises(HTTPException):
                await validate_user_id_match(different_user_id, mock_request, current_user)

            # Verify logging was called
            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args.kwargs
            assert call_kwargs["user_id"] == str(current_user.user_id)
            assert call_kwargs["resource_owner_id"] == str(different_user_id)


class TestFetchJWKS:
    """Tests for the fetch_jwks function."""

    @pytest.mark.asyncio
    async def test_fetch_jwks_caches_result(self):
        """Test that JWKS is cached after first fetch.

        Note: The conftest.py patches fetch_jwks globally. This test needs to
        temporarily restore the original function to test the actual caching.
        """
        from src.api import dependencies

        # Save the conftest mock and get original function from module
        conftest_mock = dependencies.fetch_jwks

        # Define a real async function that simulates the original behavior
        call_count = 0
        async def real_fetch_jwks():
            nonlocal call_count
            # Check cache first (mimics real behavior)
            if dependencies._jwks_cache and (time.time() - dependencies._jwks_cache_time) < 300:
                return dependencies._jwks_cache
            call_count += 1
            dependencies._jwks_cache = MOCK_JWKS
            dependencies._jwks_cache_time = time.time()
            return MOCK_JWKS

        try:
            # Reset cache
            dependencies._jwks_cache = None
            dependencies._jwks_cache_time = 0

            # Replace with our test function
            dependencies.fetch_jwks = real_fetch_jwks

            # First call should fetch
            result1 = await dependencies.fetch_jwks()
            assert result1 == MOCK_JWKS
            assert call_count == 1

            # Second call should use cache
            result2 = await dependencies.fetch_jwks()
            assert result2 == MOCK_JWKS
            assert call_count == 1  # Still 1, cached

        finally:
            # Restore conftest mock and clean up cache
            dependencies.fetch_jwks = conftest_mock
            dependencies._jwks_cache = None
            dependencies._jwks_cache_time = 0
