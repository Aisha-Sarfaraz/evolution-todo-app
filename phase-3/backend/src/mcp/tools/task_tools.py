"""T030-T032: MCP tools for task CRUD operations.

Each tool is decorated with @mcp.tool() and operates with user_id isolation.
All tools accept an optional _session parameter for testing.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Phase II imports
from src.models.task import Task, TaskStatus, TaskPriority


async def create_task(
    title: str,
    user_id: str,
    description: Optional[str] = None,
    priority: str = "Medium",
    _session: Optional[AsyncSession] = None,
) -> str:
    """Create a new task for the user.

    Args:
        title: Task title (required, 1-200 characters).
        user_id: Owner user ID for isolation.
        description: Optional task description (max 2000 characters).
        priority: Task priority - Low, Medium, High, or Urgent. Defaults to Medium.
        _session: Optional session override for testing.

    Returns:
        Confirmation message with task details.
    """
    # Validate title
    title = title.strip() if title else ""
    if not title:
        return "Error: Task title cannot be empty."
    if len(title) > 200:
        return "Error: Task title cannot exceed 200 characters."

    # Validate priority
    try:
        task_priority = TaskPriority(priority)
    except ValueError:
        return f"Error: Invalid priority '{priority}'. Use Low, Medium, High, or Urgent."

    # Truncate description
    if description and len(description) > 2000:
        description = description[:2000]

    # Use naive UTC datetime for database compatibility
    now = datetime.utcnow()

    if _session is not None:
        # Use provided session (for testing)
        task = Task(
            id=uuid4(),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=task_priority,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        _session.add(task)
        await _session.commit()
        return f"Created task: '{title}' (Priority: {priority}, ID: {task.id})"

    # Use session maker directly with async with
    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        task = Task(
            id=uuid4(),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=task_priority,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        session.add(task)
        await session.commit()
        return f"Created task: '{title}' (Priority: {priority}, ID: {task.id})"


async def _list_tasks_impl(
    session: AsyncSession,
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None,
) -> str:
    """Internal implementation of list_tasks with a provided session."""
    query = select(Task).where(Task.user_id == user_id)

    if status:
        try:
            task_status = TaskStatus(status)
            query = query.where(Task.status == task_status)
        except ValueError:
            return f"Error: Invalid status '{status}'. Use pending or complete."

    if priority:
        try:
            task_priority = TaskPriority(priority)
            query = query.where(Task.priority == task_priority)
        except ValueError:
            return f"Error: Invalid priority '{priority}'. Use Low, Medium, High, or Urgent."

    if search:
        search_term = f"%{search}%"
        query = query.where(
            Task.title.ilike(search_term) | Task.description.ilike(search_term)
        )

    # T098: Date range filters for due_date
    if due_date_from:
        try:
            from_dt = datetime.fromisoformat(due_date_from.replace("Z", "+00:00"))
            query = query.where(Task.due_date >= from_dt)
        except ValueError:
            return f"Error: Invalid due_date_from format '{due_date_from}'."

    if due_date_to:
        try:
            to_dt = datetime.fromisoformat(due_date_to.replace("Z", "+00:00"))
            query = query.where(Task.due_date <= to_dt)
        except ValueError:
            return f"Error: Invalid due_date_to format '{due_date_to}'."

    query = query.order_by(Task.created_at.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    if not tasks:
        return "No tasks found. You can create one by telling me what you need to do."

    lines = [f"Found {len(tasks)} task(s):\n"]
    for t in tasks:
        status_icon = "✓" if t.status == TaskStatus.COMPLETE else "○"
        lines.append(
            f"  {status_icon} [{t.priority.value}] {t.title} (ID: {t.id})"
        )
        if t.description:
            lines.append(f"    {t.description[:100]}...")

    return "\n".join(lines)


async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None,
    _session: Optional[AsyncSession] = None,
) -> str:
    """List tasks for the user with optional filters.

    Args:
        user_id: Owner user ID for isolation.
        status: Filter by status (pending/complete).
        priority: Filter by priority (Low/Medium/High/Urgent).
        search: Search in title and description.
        due_date_from: ISO date string for range start (inclusive).
        due_date_to: ISO date string for range end (inclusive).
        _session: Optional session override for testing.

    Returns:
        Formatted list of matching tasks or empty message.
    """
    if _session is not None:
        return await _list_tasks_impl(
            _session, user_id, status, priority, search, due_date_from, due_date_to
        )

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _list_tasks_impl(
            session, user_id, status, priority, search, due_date_from, due_date_to
        )


async def _update_task_impl(
    session: AsyncSession,
    task_id: str,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Internal implementation of update_task with a provided session."""
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return f"Error: Invalid task ID '{task_id}'."

    result = await session.execute(
        select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        return f"Error: Task not found or you don't have access to it."

    if title is not None:
        title = title.strip()
        if not title:
            return "Error: Task title cannot be empty."
        if len(title) > 200:
            return "Error: Task title cannot exceed 200 characters."
        task.title = title

    if description is not None:
        if len(description) > 2000:
            description = description[:2000]
        task.description = description

    if priority is not None:
        try:
            task.priority = TaskPriority(priority)
        except ValueError:
            return f"Error: Invalid priority '{priority}'. Use Low, Medium, High, or Urgent."

    task.updated_at = datetime.utcnow()
    await session.commit()

    return f"Updated task: '{task.title}' (Priority: {task.priority.value})"


async def update_task(
    task_id: str,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    _session: Optional[AsyncSession] = None,
) -> str:
    """Update an existing task.

    Args:
        task_id: UUID of the task to update.
        user_id: Owner user ID for isolation.
        title: New title (optional).
        description: New description (optional).
        priority: New priority (optional).
        _session: Optional session override for testing.

    Returns:
        Confirmation or error message.
    """
    if _session is not None:
        return await _update_task_impl(_session, task_id, user_id, title, description, priority)

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _update_task_impl(session, task_id, user_id, title, description, priority)


async def _complete_task_impl(
    session: AsyncSession,
    task_id: str,
    user_id: str,
) -> str:
    """Internal implementation of complete_task with a provided session."""
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

    task.status = TaskStatus.COMPLETE
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    await session.commit()

    return f"Completed task: '{task.title}'"


async def complete_task(
    task_id: str,
    user_id: str,
    _session: Optional[AsyncSession] = None,
) -> str:
    """Mark a task as complete.

    Args:
        task_id: UUID of the task to complete.
        user_id: Owner user ID for isolation.
        _session: Optional session override for testing.

    Returns:
        Confirmation or error message.
    """
    if _session is not None:
        return await _complete_task_impl(_session, task_id, user_id)

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _complete_task_impl(session, task_id, user_id)


async def _delete_task_impl(
    session: AsyncSession,
    task_id: str,
    user_id: str,
) -> str:
    """Internal implementation of delete_task with a provided session."""
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

    task_title = task.title
    await session.delete(task)
    await session.commit()

    return f"Deleted task: '{task_title}'"


async def delete_task(
    task_id: str,
    user_id: str,
    _session: Optional[AsyncSession] = None,
) -> str:
    """Permanently delete a task (hard delete).

    Args:
        task_id: UUID of the task to delete.
        user_id: Owner user ID for isolation.
        _session: Optional session override for testing.

    Returns:
        Confirmation or error message.
    """
    if _session is not None:
        return await _delete_task_impl(_session, task_id, user_id)

    from src.mcp.database import get_mcp_session_maker
    async with get_mcp_session_maker()() as session:
        return await _delete_task_impl(session, task_id, user_id)
