"""Shared pytest fixtures for Phase 2 backend tests.

Updated to work with Better Auth JWKS-based JWT verification.
"""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4, UUID
import time
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

# Load .env file from backend directory
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Set test environment
os.environ["ENVIRONMENT"] = "test"
# Allow HS256 algorithm for testing (uses symmetric keys)
os.environ["ALLOWED_JWT_ALGORITHMS"] = "RS256,ES256,EdDSA,HS256"

# Test JWT secret for mocking JWKS
TEST_JWT_SECRET = "test-secret-key-for-integration-testing-only"
MOCK_JWKS = {
    "keys": [
        {
            "kty": "oct",
            "kid": "test-key-1",
            "k": TEST_JWT_SECRET,
        }
    ]
}


def create_test_jwt(user_id: str, email: str, token_type: str = "access") -> str:
    """Create a JWT token for testing.

    Creates tokens with the proper claims for Better Auth JWKS verification.
    """
    from jose import jwt

    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + 3600,  # 1 hour
        "iss": "http://localhost:3000",
        "aud": "http://localhost:3000",
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


# Patch at module import level to avoid async issues
_original_fetch_jwks = None
_original_get_signing_key = None


def _mock_fetch_jwks():
    """Return a coroutine that returns mock JWKS."""
    async def _inner():
        return MOCK_JWKS
    return _inner()


def _mock_get_signing_key(jwks, token):
    """Return the test secret key."""
    return TEST_JWT_SECRET


# Apply patches when module loads
def setup_module_patches():
    """Setup module-level patches for JWKS verification."""
    global _original_fetch_jwks, _original_get_signing_key

    from src.api import dependencies

    _original_fetch_jwks = dependencies.fetch_jwks
    _original_get_signing_key = dependencies.get_signing_key

    # Replace with mocks
    dependencies.fetch_jwks = _mock_fetch_jwks
    dependencies.get_signing_key = _mock_get_signing_key


def teardown_module_patches():
    """Restore original functions."""
    global _original_fetch_jwks, _original_get_signing_key

    from src.api import dependencies

    if _original_fetch_jwks:
        dependencies.fetch_jwks = _original_fetch_jwks
    if _original_get_signing_key:
        dependencies.get_signing_key = _original_get_signing_key


# Apply patches immediately
try:
    setup_module_patches()
except ImportError:
    pass  # Module not yet available


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_patches():
    """Ensure patches are applied for the entire test session."""
    setup_module_patches()
    yield
    teardown_module_patches()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for API testing with real database."""
    # Import here to avoid circular imports
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def test_user_id():
    """Generate a test user ID."""
    return str(uuid4())


@pytest.fixture
def test_user_data():
    """Generate test user data."""
    return {
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": "SecurePass123!",
        "name": "Test User",
    }


@pytest_asyncio.fixture
async def authenticated_user(async_client: AsyncClient):
    """Create a test user and return user_id and auth headers using the auth endpoints.

    Uses the actual auth endpoints to create a user and get a valid JWT token.
    This ensures tests use the same authentication flow as production.
    """
    from sqlalchemy import text
    from src.database import async_session_maker

    # Generate unique email for this test
    unique_id = uuid4().hex[:8]
    email = f"test_{unique_id}@example.com"
    password = "SecurePass123!"

    # Sign up via auth endpoint
    signup_response = await async_client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": password,
            "password_confirm": password,
            "name": "Test User"
        }
    )

    # Get user_id from signup response
    if signup_response.status_code == 201:
        user_id = signup_response.json().get("user_id")

        # Mark email as verified for testing
        async with async_session_maker() as session:
            await session.execute(
                text("UPDATE users SET email_verified = true WHERE email = :email"),
                {"email": email}
            )
            await session.commit()
    else:
        # User might already exist, continue to signin
        user_id = None

    # Sign in to get access token
    signin_response = await async_client.post(
        "/api/auth/signin",
        json={
            "email": email,
            "password": password,
        }
    )
    assert signin_response.status_code == 200, f"Signin failed: {signin_response.text}"
    signin_data = signin_response.json()

    # Get user_id from the backend-issued JWT
    backend_token = signin_data.get("access_token")
    import jwt as pyjwt
    payload = pyjwt.decode(backend_token, options={"verify_signature": False})
    user_id = payload.get("sub")

    assert user_id is not None, "No user_id found"

    # Create a test JWT that works with mocked JWKS
    access_token = create_test_jwt(user_id, email)

    return {
        "user_id": user_id,
        "email": email,
        "auth_headers": {"Authorization": f"Bearer {access_token}"}
    }


@pytest_asyncio.fixture
async def authenticated_other_user(async_client: AsyncClient):
    """Create a second test user for cross-user testing.

    Uses the actual auth endpoints to create a user and get a valid JWT token.
    """
    import jwt as pyjwt
    from sqlalchemy import text
    from src.database import async_session_maker

    # Generate unique email for this test
    unique_id = uuid4().hex[:8]
    email = f"other_{unique_id}@example.com"
    password = "SecurePass123!"

    # Sign up via auth endpoint
    signup_response = await async_client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": password,
            "password_confirm": password,
            "name": "Other User"
        }
    )

    # Get user_id from signup response
    if signup_response.status_code == 201:
        user_id = signup_response.json().get("user_id")

        # Mark email as verified for testing
        async with async_session_maker() as session:
            await session.execute(
                text("UPDATE users SET email_verified = true WHERE email = :email"),
                {"email": email}
            )
            await session.commit()
    else:
        user_id = None

    # Sign in to get access token
    signin_response = await async_client.post(
        "/api/auth/signin",
        json={
            "email": email,
            "password": password,
        }
    )
    assert signin_response.status_code == 200, f"Signin failed: {signin_response.text}"
    signin_data = signin_response.json()

    # Get user_id from the backend-issued JWT
    backend_token = signin_data.get("access_token")
    payload = pyjwt.decode(backend_token, options={"verify_signature": False})
    user_id = payload.get("sub")

    assert user_id is not None, "No user_id found"

    # Create a test JWT that works with mocked JWKS
    access_token = create_test_jwt(user_id, email)

    return {
        "user_id": user_id,
        "email": email,
        "auth_headers": {"Authorization": f"Bearer {access_token}"}
    }
