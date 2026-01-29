"""Database connection and session management with async SQLAlchemy."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlmodel import SQLModel
import os


# Get database URL from environment variable and ensure async driver
_raw_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/todo_db")
# Convert postgresql:// to postgresql+asyncpg:// for async support
if _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgres://"):
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url

# Remove incompatible parameters for asyncpg (sslmode -> ssl, remove channel_binding)
# asyncpg uses 'ssl=require' instead of 'sslmode=require'
if "sslmode=" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sslmode=require", "ssl=require")
    DATABASE_URL = DATABASE_URL.replace("sslmode=prefer", "ssl=prefer")
    DATABASE_URL = DATABASE_URL.replace("sslmode=disable", "ssl=disable")
# Remove channel_binding as it's not supported by asyncpg
if "channel_binding=" in DATABASE_URL:
    import re
    DATABASE_URL = re.sub(r"[&?]channel_binding=[^&]*", "", DATABASE_URL)

# Create async engine with connection pooling
# Pool settings: min 5, max 20 connections, 30s timeout
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging for performance (enable manually for debugging)
    pool_size=5,  # Minimum connections in pool
    max_overflow=15,  # Maximum additional connections (total: 20)
    pool_timeout=30,  # Timeout waiting for connection (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Validate connections before checkout
    poolclass=AsyncAdaptedQueuePool,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions.

    Yields:
        AsyncSession: Database session for the request

    Usage:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(User))
            return result.scalars().all()

    Note:
        - Sessions are automatically closed after the request
        - Transactions are committed on success, rolled back on exception
        - Connection pooling managed by the engine
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in SQLModel metadata.
    Should only be used in development/testing.
    For production, use Alembic migrations instead.

    Usage:
        @app.on_event("startup")
        async def on_startup():
            await init_db()
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections.

    Disposes the engine and closes all pooled connections.
    Should be called on application shutdown.

    Usage:
        @app.on_event("shutdown")
        async def on_shutdown():
            await close_db()
    """
    await engine.dispose()
