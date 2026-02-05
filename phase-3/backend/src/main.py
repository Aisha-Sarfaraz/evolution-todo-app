"""T020/T069/T099/T104/T105: Phase III FastAPI application entry point.

Chat-only backend for AI-powered conversational todo management.
Imports shared infrastructure from Phase II (database, auth, middleware).
Configures APScheduler for recurrence and reminder background jobs.
Structured JSON logging and enhanced health check.
"""

import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv

# Load .env from phase-3/backend/ directory
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Phase II shared imports
from src.database import close_db

# Phase III imports
from src.agent.config import configure_agent_client
from src.api.routes.chat import router as chat_router
from src.api.routes.chatkit import router as chatkit_router
from src.api.routes.conversations import router as conversations_router
from src.api.routes.push import router as push_router
from src.logging_config import configure_logging
from src.mcp.database import close_mcp_db
from src.scheduler.jobs import check_recurrence
from src.services.reminder_service import check_reminders

# T099: Configure structured logging before anything else
configure_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    json_output=os.getenv("LOG_FORMAT", "json") == "json",
)

logger = logging.getLogger("main")

# APScheduler instance
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    # Startup
    configure_agent_client()

    # T104: Run catch-up on startup for any jobs missed while offline
    logger.info("Running startup catch-up for missed recurrence/reminder jobs")
    try:
        await check_recurrence()
    except Exception as e:
        logger.error("Startup recurrence catch-up failed: %s", e)
    try:
        await check_reminders()
    except Exception as e:
        logger.error("Startup reminder catch-up failed: %s", e)

    # Configure scheduler jobs with misfire_grace_time for catch-up
    recurrence_interval = int(os.getenv("SCHEDULER_RECURRENCE_INTERVAL_MINUTES", "5"))
    scheduler.add_job(
        check_recurrence,
        "interval",
        minutes=recurrence_interval,
        id="check_recurrence",
        replace_existing=True,
        misfire_grace_time=recurrence_interval * 60,
    )
    reminder_interval = int(os.getenv("SCHEDULER_REMINDER_INTERVAL_SECONDS", "60"))
    scheduler.add_job(
        check_reminders,
        "interval",
        seconds=reminder_interval,
        id="check_reminders",
        replace_existing=True,
        misfire_grace_time=reminder_interval * 2,
    )
    scheduler.start()
    logger.info(
        "Scheduler started: recurrence every %d min, reminders every %d sec",
        recurrence_interval,
        reminder_interval,
    )

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    await close_mcp_db()
    await close_db()


app = FastAPI(
    title="Todo AI Chatbot API",
    description="Phase III - Conversational todo management via AI chat",
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


# Register routers
app.include_router(chat_router)
app.include_router(chatkit_router)
app.include_router(conversations_router)
app.include_router(push_router)


@app.get("/health")
async def health_check() -> dict:
    """T105: Enhanced health check with component status."""
    from datetime import datetime, timezone as tz

    components: dict = {}

    # Check database
    try:
        from src.database import get_session

        async for session in get_session():
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            components["database"] = "healthy"
            break
    except Exception:
        components["database"] = "unhealthy"

    # Check scheduler
    components["scheduler"] = "running" if scheduler.running else "stopped"

    # Check MCP server connectivity
    mcp_port = os.getenv("MCP_PORT", "8001")
    mcp_host = os.getenv("MCP_HOST", "localhost")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"http://{mcp_host}:{mcp_port}/health")
            components["mcp_server"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except Exception:
        components["mcp_server"] = "unreachable"

    overall = "healthy" if components.get("database") == "healthy" else "degraded"

    return {
        "status": overall,
        "service": "todo-chatbot-api",
        "version": "3.0.0",
        "timestamp": datetime.now(tz.utc).isoformat(),
        "components": components,
    }
