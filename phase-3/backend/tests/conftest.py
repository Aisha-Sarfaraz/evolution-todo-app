"""Root conftest for Phase III backend tests."""

import asyncio
import sys
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure Phase II and Phase III import aliases are available
# This triggers the import strategy defined in phase-3/backend/src/__init__.py
_src_dir = Path(__file__).resolve().parent.parent / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

import src  # noqa: F401 — triggers phase2_backend/phase3_backend registration


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


@pytest.fixture
def mock_openrouter_client() -> MagicMock:
    """Mock OpenRouter/OpenAI client."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def sample_user_id() -> str:
    """Sample user ID for testing."""
    return "test-user-abc123"


@pytest.fixture
def sample_conversation_id() -> str:
    """Sample conversation UUID for testing."""
    return "550e8400-e29b-41d4-a716-446655440000"
