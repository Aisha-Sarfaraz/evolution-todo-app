"""T033-T034: FastMCP server definition with task CRUD tools.

Standalone MCP server using Streamable HTTP transport.
Registers all task tools and includes invocation logging middleware.
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from phase-3/backend/ directory
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

from mcp.server.fastmcp import FastMCP

# Import Category model to ensure SQLAlchemy can resolve Task's foreign key
from src.models.category import Category  # noqa: F401

from src.mcp.tools.task_tools import (
    create_task,
    complete_task,
    delete_task,
    list_tasks,
    update_task,
)
from src.mcp.tools.recurrence_tools import (
    create_recurrence,
    remove_recurrence,
    update_recurrence,
)
from src.mcp.tools.reminder_tools import set_due_date

logger = logging.getLogger("mcp.server")

# Create FastMCP server instance
mcp = FastMCP(
    name="todo-mcp-server",
    instructions="MCP server for todo task management operations.",
)


def _log_tool_call(
    user_id: str,
    tool_name: str,
    tool_input: dict,
    tool_output: str,
    duration_ms: float,
    success: bool,
) -> None:
    """T034: Log tool invocations per FR-019."""
    logger.info(
        "tool_invocation",
        extra={
            "user_id": user_id,
            "tool": tool_name,
            "input": tool_input,
            "output": tool_output[:500],
            "duration_ms": round(duration_ms, 2),
            "success": success,
        },
    )


@mcp.tool()
async def mcp_create_task(
    title: str,
    user_id: str,
    description: Optional[str] = None,
    priority: str = "Medium",
) -> str:
    """Create a new task for the user.

    Args:
        title: Task title (1-200 characters, required).
        user_id: The user's ID.
        description: Optional description (max 2000 chars).
        priority: Low, Medium, High, or Urgent. Defaults to Medium.
    """
    start = time.monotonic()
    try:
        result = await create_task(title=title, user_id=user_id, description=description, priority=priority)
        _log_tool_call(user_id, "create_task", {"title": title, "priority": priority}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "create_task", {"title": title}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error creating task: {e}"


@mcp.tool()
async def mcp_list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
) -> str:
    """List tasks with optional filters.

    Args:
        user_id: The user's ID.
        status: Filter by status (pending or complete).
        priority: Filter by priority (Low, Medium, High, Urgent).
        search: Search keyword in title and description.
    """
    start = time.monotonic()
    try:
        result = await list_tasks(user_id=user_id, status=status, priority=priority, search=search)
        _log_tool_call(user_id, "list_tasks", {"status": status, "priority": priority, "search": search}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "list_tasks", {}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error listing tasks: {e}"


@mcp.tool()
async def mcp_update_task(
    task_id: str,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Update an existing task's details.

    Args:
        task_id: UUID of the task to update.
        user_id: The user's ID.
        title: New title (optional).
        description: New description (optional).
        priority: New priority (optional).
    """
    start = time.monotonic()
    try:
        result = await update_task(task_id=task_id, user_id=user_id, title=title, description=description, priority=priority)
        _log_tool_call(user_id, "update_task", {"task_id": task_id}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "update_task", {"task_id": task_id}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error updating task: {e}"


@mcp.tool()
async def mcp_complete_task(
    task_id: str,
    user_id: str,
) -> str:
    """Mark a task as complete.

    Args:
        task_id: UUID of the task to complete.
        user_id: The user's ID.
    """
    start = time.monotonic()
    try:
        result = await complete_task(task_id=task_id, user_id=user_id)
        _log_tool_call(user_id, "complete_task", {"task_id": task_id}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "complete_task", {"task_id": task_id}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error completing task: {e}"


@mcp.tool()
async def mcp_delete_task(
    task_id: str,
    user_id: str,
) -> str:
    """Permanently delete a task.

    Args:
        task_id: UUID of the task to delete.
        user_id: The user's ID.
    """
    start = time.monotonic()
    try:
        result = await delete_task(task_id=task_id, user_id=user_id)
        _log_tool_call(user_id, "delete_task", {"task_id": task_id}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "delete_task", {"task_id": task_id}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error deleting task: {e}"


@mcp.tool()
async def mcp_create_recurrence(
    task_id: str,
    user_id: str,
    frequency: str,
    interval: int = 1,
    end_date_str: Optional[str] = None,
) -> str:
    """Create a recurring schedule for a task.

    Args:
        task_id: UUID of the task to make recurring.
        user_id: The user's ID.
        frequency: daily, weekly, monthly, or yearly.
        interval: How often (1 = every period, 2 = every other).
        end_date_str: Optional end date in YYYY-MM-DD format.
    """
    start = time.monotonic()
    try:
        result = await create_recurrence(task_id=task_id, user_id=user_id, frequency=frequency, interval=interval, end_date_str=end_date_str)
        _log_tool_call(user_id, "create_recurrence", {"task_id": task_id, "frequency": frequency}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "create_recurrence", {"task_id": task_id}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error creating recurrence: {e}"


@mcp.tool()
async def mcp_update_recurrence(
    task_id: str,
    user_id: str,
    frequency: Optional[str] = None,
    interval: Optional[int] = None,
    end_date_str: Optional[str] = None,
) -> str:
    """Update an existing recurrence rule.

    Args:
        task_id: UUID of the recurring task.
        user_id: The user's ID.
        frequency: New frequency (optional).
        interval: New interval (optional).
        end_date_str: New end date (optional).
    """
    start = time.monotonic()
    try:
        result = await update_recurrence(task_id=task_id, user_id=user_id, frequency=frequency, interval=interval, end_date_str=end_date_str)
        _log_tool_call(user_id, "update_recurrence", {"task_id": task_id}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "update_recurrence", {"task_id": task_id}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error updating recurrence: {e}"


@mcp.tool()
async def mcp_remove_recurrence(
    task_id: str,
    user_id: str,
) -> str:
    """Remove a recurring schedule from a task.

    Args:
        task_id: UUID of the recurring task.
        user_id: The user's ID.
    """
    start = time.monotonic()
    try:
        result = await remove_recurrence(task_id=task_id, user_id=user_id)
        _log_tool_call(user_id, "remove_recurrence", {"task_id": task_id}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "remove_recurrence", {"task_id": task_id}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error removing recurrence: {e}"


@mcp.tool()
async def mcp_set_due_date(
    task_id: str,
    user_id: str,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
) -> str:
    """Set a due date and/or reminder for a task.

    Args:
        task_id: UUID of the task.
        user_id: The user's ID.
        due_date: ISO datetime for when the task is due (e.g., 2026-02-15T14:00:00Z).
        reminder_time: ISO datetime for when to send a notification.
    """
    start = time.monotonic()
    try:
        result = await set_due_date(task_id=task_id, user_id=user_id, due_date=due_date, reminder_time=reminder_time)
        _log_tool_call(user_id, "set_due_date", {"task_id": task_id, "due_date": due_date}, result, (time.monotonic() - start) * 1000, True)
        return result
    except Exception as e:
        _log_tool_call(user_id, "set_due_date", {"task_id": task_id}, str(e), (time.monotonic() - start) * 1000, False)
        return f"Error setting due date: {e}"


def get_mcp_app():
    """Get the MCP ASGI app for use with uvicorn."""
    return mcp.streamable_http_app()


def run_mcp_server() -> None:
    """Run the MCP server with Streamable HTTP transport via uvicorn."""
    import uvicorn
    port = int(os.getenv("MCP_PORT", "8001"))
    host = os.getenv("MCP_HOST", "localhost")
    uvicorn.run(
        "src.mcp.server:get_mcp_app",
        factory=True,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    run_mcp_server()
