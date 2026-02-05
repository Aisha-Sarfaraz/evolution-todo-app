"""T066: MCP tools for recurrence management.

create_recurrence, update_recurrence, remove_recurrence with user isolation.
"""

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.recurrence import RecurrenceRule
from src.services.recurrence_service import calculate_next_occurrence


async def _create_recurrence_impl(
    session: AsyncSession,
    task_id: str,
    user_id: str,
    frequency: str,
    interval: int = 1,
    days_of_week: Optional[list[int]] = None,
    day_of_month: Optional[int] = None,
    end_date_str: Optional[str] = None,
) -> str:
    """Internal implementation of create_recurrence with a provided session."""
    # Validate frequency
    if frequency not in ("daily", "weekly", "monthly", "yearly"):
        return f"Error: Invalid frequency '{frequency}'. Use daily, weekly, monthly, or yearly."

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

    # Check for existing rule
    existing = await session.execute(
        select(RecurrenceRule).where(RecurrenceRule.task_id == task_uuid)
    )
    if existing.scalar_one_or_none():
        return "Error: This task already has a recurrence rule. Update or remove it first."

    # Parse end date
    end_date = None
    if end_date_str:
        try:
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            return f"Error: Invalid end date format '{end_date_str}'. Use YYYY-MM-DD."

    # Calculate first next occurrence
    now = datetime.now(timezone.utc)
    next_occ = calculate_next_occurrence(
        frequency, interval, now, end_date, days_of_week, day_of_month
    )
    if not next_occ:
        return "Error: End date is in the past. No occurrences would be created."

    rule = RecurrenceRule(
        id=uuid4(),
        task_id=task_uuid,
        frequency=frequency,
        interval=interval,
        days_of_week=days_of_week,
        day_of_month=day_of_month,
        end_date=end_date,
        next_occurrence=next_occ,
    )

    session.add(rule)
    await session.commit()

    interval_text = f"every {interval} " if interval > 1 else "every "
    freq_text = frequency if interval == 1 else frequency.rstrip("y") + "ies" if frequency.endswith("y") else frequency + "s"
    end_text = f" until {end_date}" if end_date else ""

    return f"Set '{task.title}' to recur {interval_text}{freq_text}{end_text}. Next occurrence: {next_occ.strftime('%Y-%m-%d %H:%M')} UTC."


async def create_recurrence(
    task_id: str,
    user_id: str,
    frequency: str,
    interval: int = 1,
    days_of_week: Optional[list[int]] = None,
    day_of_month: Optional[int] = None,
    end_date_str: Optional[str] = None,
    _session: Optional[AsyncSession] = None,
) -> str:
    """Create a recurrence rule for a task.

    Args:
        task_id: UUID of the task.
        user_id: Owner user ID.
        frequency: daily, weekly, monthly, or yearly.
        interval: How often (default: 1).
        days_of_week: Weekday integers for weekly.
        day_of_month: Day for monthly.
        end_date_str: Optional end date (YYYY-MM-DD).
        _session: Optional session override for testing.
    """
    if _session is not None:
        return await _create_recurrence_impl(
            _session, task_id, user_id, frequency, interval, days_of_week, day_of_month, end_date_str
        )

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _create_recurrence_impl(
            session, task_id, user_id, frequency, interval, days_of_week, day_of_month, end_date_str
        )


async def _update_recurrence_impl(
    session: AsyncSession,
    task_id: str,
    user_id: str,
    frequency: Optional[str] = None,
    interval: Optional[int] = None,
    end_date_str: Optional[str] = None,
) -> str:
    """Internal implementation of update_recurrence with a provided session."""
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return f"Error: Invalid task ID '{task_id}'."

    # Verify ownership via task
    task_result = await session.execute(
        select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
    )
    if not task_result.scalar_one_or_none():
        return "Error: Task not found or you don't have access to it."

    result = await session.execute(
        select(RecurrenceRule).where(RecurrenceRule.task_id == task_uuid)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        return "Error: No recurrence rule found for this task."

    if frequency:
        if frequency not in ("daily", "weekly", "monthly", "yearly"):
            return f"Error: Invalid frequency '{frequency}'."
        rule.frequency = frequency

    if interval is not None:
        if interval < 1:
            return "Error: Interval must be at least 1."
        rule.interval = interval

    if end_date_str:
        try:
            rule.end_date = date.fromisoformat(end_date_str)
        except ValueError:
            return f"Error: Invalid end date format '{end_date_str}'."

    # Recalculate next occurrence
    now = datetime.now(timezone.utc)
    next_occ = calculate_next_occurrence(
        rule.frequency, rule.interval, now, rule.end_date
    )
    if next_occ:
        rule.next_occurrence = next_occ

    await session.commit()
    return f"Updated recurrence rule: {rule.frequency} every {rule.interval}."


async def update_recurrence(
    task_id: str,
    user_id: str,
    frequency: Optional[str] = None,
    interval: Optional[int] = None,
    end_date_str: Optional[str] = None,
    _session: Optional[AsyncSession] = None,
) -> str:
    """Update an existing recurrence rule."""
    if _session is not None:
        return await _update_recurrence_impl(_session, task_id, user_id, frequency, interval, end_date_str)

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _update_recurrence_impl(session, task_id, user_id, frequency, interval, end_date_str)


async def _remove_recurrence_impl(
    session: AsyncSession,
    task_id: str,
    user_id: str,
) -> str:
    """Internal implementation of remove_recurrence with a provided session."""
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return f"Error: Invalid task ID '{task_id}'."

    # Verify ownership
    task_result = await session.execute(
        select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
    )
    if not task_result.scalar_one_or_none():
        return "Error: Task not found or you don't have access to it."

    result = await session.execute(
        select(RecurrenceRule).where(RecurrenceRule.task_id == task_uuid)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        return "Error: No recurrence rule found for this task."

    await session.delete(rule)
    await session.commit()
    return "Recurrence removed. No more recurring instances will be created."


async def remove_recurrence(
    task_id: str,
    user_id: str,
    _session: Optional[AsyncSession] = None,
) -> str:
    """Remove a recurrence rule from a task."""
    if _session is not None:
        return await _remove_recurrence_impl(_session, task_id, user_id)

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _remove_recurrence_impl(session, task_id, user_id)
