"""Phase III FastAPI application entry point.

Chat backend with embedded MCP server for AI-powered task management.
"""

import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv

# Load .env from phase-3/backend/ directory if it exists
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agent.config import configure_agent_client
from src.api.routes.chatkit import router as chatkit_router
from src.logging_config import configure_logging
from src.mcp_tools.database import close_mcp_db
from src.mcp_tools.server import mcp

# Configure structured logging
configure_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    json_output=os.getenv("LOG_FORMAT", "json") == "json",
)

logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    # Startup
    configure_agent_client()
    logger.info("Agent client configured")
    logger.info("MCP server embedded at /mcp")

    yield

    # Shutdown
    await close_mcp_db()
    logger.info("Database connections closed")


app = FastAPI(
    title="Todo AI Chatbot API",
    description="Phase III - Conversational todo management via AI chat with MCP",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS configuration - allow Vercel frontend and localhost
default_origins = ",".join([
    "http://localhost:3000",
    "https://frontend-sable-seven-72.vercel.app",
    "https://frontend-aishas-projects-cb1df1f3.vercel.app",
    "https://frontend-aisha-sarfaraz-aishas-projects-cb1df1f3.vercel.app",
])
allowed_origins = os.getenv("ALLOWED_ORIGINS", default_origins).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register chatkit router
app.include_router(chatkit_router)

# Mount MCP server at /mcp
mcp_app = mcp.streamable_http_app()
app.mount("/mcp", mcp_app)


@app.get("/health")
async def health_check() -> dict:
    """Legacy health check endpoint (backward compatibility)."""
    from datetime import datetime, timezone as tz

    return {
        "status": "healthy",
        "service": "todo-chatbot-api",
        "version": "3.0.0",
        "timestamp": datetime.now(tz.utc).isoformat(),
        "mcp": "embedded",
    }


@app.get("/health/live")
async def health_live() -> dict:
    """Liveness probe: is the process alive? No dependency checks."""
    return {
        "status": "alive",
        "service": "todo-chatbot-api",
        "version": "3.0.0",
    }


@app.get("/health/ready")
async def health_ready():
    """Readiness probe: can the service handle traffic? Checks DB connectivity."""
    from fastapi.responses import JSONResponse
    from sqlalchemy import text
    from src.database import async_session_maker

    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "disconnected"},
        )


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Todo AI Chatbot API with MCP",
        "docs": "/docs",
        "health": "/health",
        "mcp": "/mcp",
    }
