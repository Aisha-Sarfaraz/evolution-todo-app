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
from src.mcp.database import close_mcp_db
from src.mcp.server import mcp

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

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
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
    """Health check endpoint."""
    from datetime import datetime, timezone as tz

    return {
        "status": "healthy",
        "service": "todo-chatbot-api",
        "version": "3.0.0",
        "timestamp": datetime.now(tz.utc).isoformat(),
        "mcp": "embedded",
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Todo AI Chatbot API with MCP",
        "docs": "/docs",
        "health": "/health",
        "mcp": "/mcp",
    }
