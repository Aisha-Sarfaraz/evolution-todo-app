"""T010: Unit tests for MCP server database session management.

Tests that the MCP server has its own independent database session
management with proper async engine and connection pooling.
"""

import os
from unittest.mock import patch, AsyncMock, MagicMock

import pytest


@pytest.mark.unit
class TestMCPDatabaseSession:
    """Tests for MCP server independent database sessions."""

    def test_mcp_engine_uses_database_url(self) -> None:
        """Verify MCP engine reads DATABASE_URL from environment."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
        }):
            from phase3_backend.mcp.database import get_mcp_database_url

            url = get_mcp_database_url()
            assert "asyncpg" in url
            assert "testdb" in url

    def test_mcp_engine_converts_postgresql_to_asyncpg(self) -> None:
        """Verify postgresql:// URLs are converted to postgresql+asyncpg://."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:pass@localhost/db",
        }):
            from phase3_backend.mcp.database import get_mcp_database_url

            url = get_mcp_database_url()
            assert url.startswith("postgresql+asyncpg://")

    def test_mcp_engine_handles_sslmode(self) -> None:
        """Verify sslmode parameter is converted to ssl for asyncpg."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:pass@host/db?sslmode=require",
        }):
            from phase3_backend.mcp.database import get_mcp_database_url

            url = get_mcp_database_url()
            assert "sslmode=" not in url
            assert "ssl=require" in url

    @pytest.mark.asyncio
    async def test_mcp_get_session_yields_session(self) -> None:
        """Verify get_mcp_session yields an async session."""
        from phase3_backend.mcp.database import get_mcp_session

        # This test validates the generator signature exists
        gen = get_mcp_session()
        assert hasattr(gen, "__aiter__") or hasattr(gen, "__anext__")
