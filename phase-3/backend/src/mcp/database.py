"""T013: MCP server independent database session management.

The MCP server runs as a separate process and needs its own database
connection pool, independent of the FastAPI backend's pool.
"""

import os
import re
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool


def get_mcp_database_url() -> str:
    """Build async database URL from DATABASE_URL environment variable.

    Converts postgresql:// to postgresql+asyncpg:// and handles
    asyncpg-incompatible parameters (sslmode → ssl, removes channel_binding).
    """
    raw_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/todo_db")

    # Convert to async driver URL
    if raw_url.startswith("postgresql://"):
        url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif raw_url.startswith("postgres://"):
        url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
    else:
        url = raw_url

    # Convert sslmode to ssl for asyncpg compatibility
    if "sslmode=" in url:
        url = url.replace("sslmode=require", "ssl=require")
        url = url.replace("sslmode=prefer", "ssl=prefer")
        url = url.replace("sslmode=disable", "ssl=disable")

    # Remove channel_binding (not supported by asyncpg)
    if "channel_binding=" in url:
        url = re.sub(r"[&?]channel_binding=[^&]*", "", url)

    return url


# Create MCP-specific async engine with its own connection pool
_mcp_engine = create_async_engine(
    get_mcp_database_url(),
    echo=False,
    pool_size=3,
    max_overflow=7,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    poolclass=AsyncAdaptedQueuePool,
)

# MCP-specific session factory
_mcp_session_maker = async_sessionmaker(
    _mcp_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_mcp_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for MCP tool operations.

    Sessions are automatically committed on success, rolled back on exception,
    and closed after use.
    """
    async with _mcp_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_mcp_session_maker():
    """Get the MCP session maker for direct session creation.

    Use this when you need more control over session lifecycle:
        async with get_mcp_session_maker()() as session:
            # do work
            await session.commit()
    """
    return _mcp_session_maker


async def close_mcp_db() -> None:
    """Dispose MCP engine and close all pooled connections."""
    await _mcp_engine.dispose()
