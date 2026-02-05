"""T082: MCP tool for setting due dates and reminders."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.reminder import ReminderMetadata


async def _set_due_date_impl(
    session: AsyncSession,
    task_id: str,
    user_id: str,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
) -> str:
    """Internal implementation of set_due_date with a provided session."""
    # Validate task ownership
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return f"Error: Invalid task ID '{task_id}'."

    result = await session.execute(
        select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        return "Error: Task not found or you don't have access to it."

    # Parse dates
    parsed_due = None
    parsed_reminder = None

    if due_date:
        try:
            parsed_due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            return f"Error: Invalid due date format '{due_date}'. Use ISO format (e.g., 2026-02-15T14:00:00Z)."

    if reminder_time:
        try:
            parsed_reminder = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))
        except ValueError:
            return f"Error: Invalid reminder time format '{reminder_time}'."

    # Check for existing reminder metadata
    existing_result = await session.execute(
        select(ReminderMetadata).where(ReminderMetadata.task_id == task_uuid)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Update existing
        if parsed_due:
            existing.due_date = parsed_due
        if parsed_reminder:
            existing.reminder_time = parsed_reminder
            existing.notification_sent = False  # Reset on update
    else:
        # Create new
        reminder = ReminderMetadata(
            id=uuid4(),
            task_id=task_uuid,
            due_date=parsed_due,
            reminder_time=parsed_reminder,
        )
        session.add(reminder)

    await session.commit()

    parts = []
    if parsed_due:
        parts.append(f"due date: {parsed_due.strftime('%Y-%m-%d %H:%M')} UTC")
    if parsed_reminder:
        parts.append(f"reminder at: {parsed_reminder.strftime('%Y-%m-%d %H:%M')} UTC")

    return f"Set {' and '.join(parts)} for '{task.title}'."


async def set_due_date(
    task_id: str,
    user_id: str,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    _session: Optional[AsyncSession] = None,
) -> str:
    """Set a due date and/or reminder time for a task.

    Args:
        task_id: UUID of the task.
        user_id: Owner user ID.
        due_date: ISO format datetime for when the task is due.
        reminder_time: ISO format datetime for when to send notification.
        _session: Optional session override for testing.

    Returns:
        Confirmation or error message.
    """
    if not due_date and not reminder_time:
        return "Error: At least one of due_date or reminder_time must be provided."

    if _session is not None:
        return await _set_due_date_impl(_session, task_id, user_id, due_date, reminder_time)

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _set_due_date_impl(session, task_id, user_id, due_date, reminder_time)
