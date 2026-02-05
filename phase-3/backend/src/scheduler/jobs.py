"""T068: Scheduler jobs for recurrence and reminders.

APScheduler jobs that run periodically to:
- Create new task instances for due recurrence rules.
- Check and send reminder notifications.
"""

import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.recurrence import RecurrenceRule
from src.services.recurrence_service import calculate_next_occurrence

logger = logging.getLogger("scheduler.jobs")


async def check_recurrence() -> None:
    """Check for due recurrence rules and create new task instances.

    Queries recurrence_rules where next_occurrence <= now,
    creates a new task instance copying the original task's details,
    and updates next_occurrence.
    """
    from src.mcp.database import get_mcp_session

    async for session in get_mcp_session():
        try:
            await _process_due_recurrences(session)
        except Exception as e:
            logger.error("Recurrence check failed: %s", e)
        break


async def _process_due_recurrences(session: AsyncSession) -> None:
    """Process all due recurrence rules."""
    now = datetime.now(timezone.utc)

    result = await session.execute(
        select(RecurrenceRule).where(RecurrenceRule.next_occurrence <= now)
    )
    due_rules = result.scalars().all()

    for rule in due_rules:
        try:
            await _create_task_instance(session, rule, now)
        except Exception as e:
            logger.error("Failed to process recurrence %s: %s", rule.id, e)

    await session.commit()


async def _create_task_instance(
    session: AsyncSession,
    rule: RecurrenceRule,
    now: datetime,
) -> None:
    """Create a new task instance from a recurrence rule."""
    # Load the original task
    result = await session.execute(
        select(Task).where(Task.id == rule.task_id)
    )
    original_task = result.scalar_one_or_none()

    if not original_task:
        logger.warning("Original task %s not found for recurrence %s", rule.task_id, rule.id)
        return

    # Create new task instance
    new_task = Task(
        id=uuid4(),
        title=original_task.title,
        description=original_task.description,
        status=TaskStatus.PENDING,
        priority=original_task.priority,
        user_id=original_task.user_id,
        category_id=original_task.category_id,
        created_at=now,
        updated_at=now,
    )
    session.add(new_task)

    # Calculate next occurrence
    next_occ = calculate_next_occurrence(
        rule.frequency,
        rule.interval,
        now,
        rule.end_date,
        rule.days_of_week,
        rule.day_of_month,
    )

    if next_occ:
        rule.next_occurrence = next_occ
    else:
        # End date reached, remove the rule
        await session.delete(rule)
        logger.info("Recurrence %s reached end date, removed", rule.id)

    logger.info(
        "Created recurring task '%s' for user %s",
        new_task.title,
        new_task.user_id,
    )
