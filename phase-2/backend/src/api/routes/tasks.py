"""Task management API routes.

T064-T069: Task CRUD endpoints with user isolation.

Endpoints:
- GET /api/{user_id}/tasks (T064)
- POST /api/{user_id}/tasks (T065)
- GET /api/{user_id}/tasks/{id} (T066)
- PUT /api/{user_id}/tasks/{id} (T067)
- DELETE /api/{user_id}/tasks/{id} (T068)
- PATCH /api/{user_id}/tasks/{id}/complete (T069)
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID  # Still needed for category_id, tag_id, task_id

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.dependencies import ValidatedUser
from src.database import get_session
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate, TaskStatus, TaskPriority
from src.models.category import Category
from src.models.tag import Tag
from src.models.task_tag import TaskTag
from src.utils.errors import ErrorCode, ErrorResponse, format_error


router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


# Response schemas

class TaskListResponse(BaseModel):
    """Response schema for task list."""
    tasks: list[TaskRead]
    total: int


class TaskWithRelations(TaskRead):
    """Task with populated category and tags."""
    category: dict | None = None
    tags: list[dict] = []


# Priority order for sorting (Urgent > High > Medium > Low)
PRIORITY_ORDER = {
    TaskPriority.LOW: 1,
    TaskPriority.MEDIUM: 2,
    TaskPriority.HIGH: 3,
    TaskPriority.URGENT: 4,
}


# T064: GET /api/{user_id}/tasks
# T123-T130: Enhanced search, filter, sort
@router.get(
    "",
    response_model=TaskListResponse,
    responses={
        200: {"description": "Tasks retrieved successfully", "model": TaskListResponse},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot access other users' tasks", "model": ErrorResponse},
    },
    summary="List tasks",
    description="List all tasks for the authenticated user with optional filtering, searching, sorting, and pagination.",
)
async def list_tasks(
    user_id: str,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    # T124: Status filter
    status_filter: str | None = Query(None, alias="status", description="Filter by task status (pending, complete, all)"),
    # T125: Priority filter (comma-separated for multiple)
    priority: str | None = Query(None, description="Filter by priority (Low,Medium,High,Urgent - comma-separated for multiple)"),
    # T126: Category filter
    category: UUID | None = Query(None, description="Filter by category ID"),
    # T127: Tags filter with AND logic
    tags: str | None = Query(None, description="Filter by tag IDs (comma-separated, AND logic)"),
    # T128: Date range filters
    created_after: datetime | None = Query(None, description="Filter tasks created after this date (ISO 8601)"),
    created_before: datetime | None = Query(None, description="Filter tasks created before this date (ISO 8601)"),
    updated_after: datetime | None = Query(None, description="Filter tasks updated after this date (ISO 8601)"),
    updated_before: datetime | None = Query(None, description="Filter tasks updated before this date (ISO 8601)"),
    completed_after: datetime | None = Query(None, description="Filter tasks completed after this date (ISO 8601)"),
    completed_before: datetime | None = Query(None, description="Filter tasks completed before this date (ISO 8601)"),
    # T123: Search
    search: str | None = Query(None, description="Search in title and description (case-insensitive)"),
    # T129: Sort
    sort_by: str = Query("created_at", description="Sort field (created_at, updated_at, priority, title)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
    # Pagination
    limit: int = Query(50, ge=1, le=100, description="Maximum results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List all tasks for the authenticated user.

    T123-T130: Enhanced task discovery with search, filter, sort.

    Search: Case-insensitive ILIKE on title and description.
    Filter: Status, priority (multiple via comma), category, tags (AND logic), date ranges.
    Sort: By created_at, updated_at, priority, or title. Default: created_at DESC.
    """
    # Build base query with user isolation
    query = select(Task).where(Task.user_id == user_id)

    # T124: Apply status filter
    if status_filter and status_filter.lower() != "all":
        if status_filter.lower() == "pending":
            query = query.where(Task.status == TaskStatus.PENDING)
        elif status_filter.lower() == "complete":
            query = query.where(Task.status == TaskStatus.COMPLETE)

    # T125: Apply priority filter (supports comma-separated values)
    if priority:
        priority_values = [p.strip() for p in priority.split(",") if p.strip()]
        if priority_values:
            # Map string values to enum
            try:
                priority_enums = [TaskPriority(p) for p in priority_values]
                query = query.where(Task.priority.in_(priority_enums))
            except ValueError:
                # Invalid priority value - ignore filter
                pass

    # T126: Apply category filter
    if category:
        query = query.where(Task.category_id == category)

    # T127: Apply tags filter with AND logic
    if tags:
        tag_ids_str = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_ids_str:
            try:
                tag_ids = [UUID(t) for t in tag_ids_str]
                # AND logic: task must have ALL specified tags
                # Join with task_tag table and count matching tags
                tag_subquery = (
                    select(TaskTag.task_id)
                    .where(TaskTag.tag_id.in_(tag_ids))
                    .group_by(TaskTag.task_id)
                    .having(func.count(TaskTag.tag_id.distinct()) == len(tag_ids))
                )
                query = query.where(Task.id.in_(tag_subquery))
            except ValueError:
                # Invalid UUID - ignore filter
                pass

    # T128: Apply date range filters
    if created_after:
        query = query.where(Task.created_at >= created_after)
    if created_before:
        query = query.where(Task.created_at <= created_before)
    if updated_after:
        query = query.where(Task.updated_at >= updated_after)
    if updated_before:
        query = query.where(Task.updated_at <= updated_before)
    if completed_after:
        query = query.where(Task.completed_at >= completed_after)
    if completed_before:
        query = query.where(Task.completed_at <= completed_before)

    # T123: Apply search (case-insensitive ILIKE on title and description)
    if search:
        # Escape special SQL characters
        search_escaped = search.replace("%", "\\%").replace("_", "\\_")
        search_term = f"%{search_escaped}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # T129: Apply sorting
    valid_sort_fields = {"created_at", "updated_at", "priority", "title"}
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"  # Default fallback

    sort_column = getattr(Task, sort_by, Task.created_at)

    # Normalize order
    order_lower = order.lower() if order else "desc"
    if order_lower not in ("asc", "desc"):
        order_lower = "desc"  # Default fallback

    if order_lower == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Apply pagination - fetch limit+1 to detect if more results exist
    query = query.offset(offset).limit(limit + 1)

    # Execute single query (avoids separate COUNT round-trip to remote DB)
    result = await session.execute(query)
    tasks = list(result.scalars().all())

    # Determine total: if we got more than limit, there are more results
    if len(tasks) > limit:
        tasks = tasks[:limit]
        # Only run COUNT query when we know there are more results
        count_query = select(func.count()).select_from(
            select(Task.id).where(Task.user_id == user_id).subquery()
        )
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
    else:
        total = offset + len(tasks)

    return TaskListResponse(
        tasks=[TaskRead.model_validate(task) for task in tasks],
        total=total,
    )


# T065: POST /api/{user_id}/tasks
@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Task created successfully", "model": TaskRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot create tasks for other users", "model": ErrorResponse},
        404: {"description": "Category not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    summary="Create task",
    description="Create a new task. Title is required (1-200 chars). Description max 2000 chars.",
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Create a new task for the authenticated user.

    Validates title, truncates description, sets defaults.
    """
    # Ensure user_id from URL matches task data (or set it)
    task_data.user_id = user_id

    # Validate category exists (if provided)
    if task_data.category_id:
        category_result = await session.execute(
            select(Category).where(
                (Category.id == task_data.category_id) &
                ((Category.user_id == user_id) | (Category.is_system == True))
            )
        )
        if not category_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=format_error(ErrorCode.CATEGORY_NOT_FOUND, "Category not found")
            )

    # Validate tags exist and belong to user (if provided)
    if task_data.tag_ids:
        tags_result = await session.execute(
            select(Tag).where(
                (Tag.id.in_(task_data.tag_ids)) & (Tag.user_id == user_id)
            )
        )
        found_tags = tags_result.scalars().all()
        if len(found_tags) != len(task_data.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=format_error(ErrorCode.TAG_NOT_FOUND, "One or more tags not found")
            )

    # Create task
    task = Task(
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description[:2000] if task_data.description else None,
        status=task_data.status,
        priority=task_data.priority,
        category_id=task_data.category_id,
    )

    session.add(task)
    await session.flush()  # Flush to get task.id before creating tag associations

    # Create tag associations if provided
    if task_data.tag_ids:
        for tag_id in task_data.tag_ids:
            task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
            session.add(task_tag)

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)


# T066: GET /api/{user_id}/tasks/{id}
@router.get(
    "/{task_id}",
    response_model=TaskRead,
    responses={
        200: {"description": "Task retrieved successfully", "model": TaskRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot access other users' tasks", "model": ErrorResponse},
        404: {"description": "Task not found", "model": ErrorResponse},
    },
    summary="Get task by ID",
    description="Retrieve a single task by its ID. Returns 404 for non-existent tasks.",
)
async def get_task(
    user_id: str,
    task_id: UUID,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Get a single task by ID.

    Returns 404 for non-existent or cross-user access (security).
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.TASK_NOT_FOUND, "Task not found")
        )

    return TaskRead.model_validate(task)


# T067: PUT /api/{user_id}/tasks/{id}
@router.put(
    "/{task_id}",
    response_model=TaskRead,
    responses={
        200: {"description": "Task updated successfully", "model": TaskRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot update other users' tasks", "model": ErrorResponse},
        404: {"description": "Task or category not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    summary="Update task",
    description="Update an existing task. Partial updates supported - only provided fields are updated.",
)
async def update_task(
    user_id: str,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Update an existing task.

    Partial updates supported - only provided fields are updated.
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.TASK_NOT_FOUND, "Task not found")
        )

    # Update fields if provided
    update_data = task_data.model_dump(exclude_unset=True)

    if "title" in update_data:
        title = update_data["title"].strip()
        if not title:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=format_error(ErrorCode.VALIDATION_ERROR, "Title cannot be empty", "title")
            )
        task.title = title

    if "description" in update_data:
        desc = update_data["description"]
        task.description = desc[:2000] if desc else None

    if "priority" in update_data:
        task.priority = update_data["priority"]

    if "status" in update_data:
        task.status = update_data["status"]

    if "category_id" in update_data:
        category_id = update_data["category_id"]
        if category_id:
            # Validate category exists
            category_result = await session.execute(
                select(Category).where(
                    (Category.id == category_id) &
                    ((Category.user_id == user_id) | (Category.is_system == True))
                )
            )
            if not category_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=format_error(ErrorCode.CATEGORY_NOT_FOUND, "Category not found")
                )
        task.category_id = category_id

    # Handle tag assignments (T109)
    if "tag_ids" in update_data:
        tag_ids = update_data["tag_ids"]
        if tag_ids is not None:
            # Validate all tags belong to the user
            if tag_ids:
                tags_result = await session.execute(
                    select(Tag).where(
                        (Tag.id.in_(tag_ids)) & (Tag.user_id == user_id)
                    )
                )
                found_tags = tags_result.scalars().all()
                if len(found_tags) != len(tag_ids):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=format_error(ErrorCode.TAG_NOT_FOUND, "One or more tags not found")
                    )

            # Delete existing task-tag associations
            existing_task_tags = await session.execute(
                select(TaskTag).where(TaskTag.task_id == task_id)
            )
            for task_tag in existing_task_tags.scalars().all():
                await session.delete(task_tag)

            # Create new task-tag associations
            for tag_id in (tag_ids or []):
                task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
                session.add(task_tag)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)


# T068: DELETE /api/{user_id}/tasks/{id}
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Task deleted successfully"},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot delete other users' tasks", "model": ErrorResponse},
        404: {"description": "Task not found", "model": ErrorResponse},
    },
    summary="Delete task",
    description="Delete a task permanently. Returns 404 for non-existent tasks.",
)
async def delete_task(
    user_id: str,
    task_id: UUID,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Delete a task.

    Returns 404 for non-existent or cross-user access.
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.TASK_NOT_FOUND, "Task not found")
        )

    await session.delete(task)
    await session.commit()

    return None


# T069: PATCH /api/{user_id}/tasks/{id}/complete
@router.patch(
    "/{task_id}/complete",
    response_model=TaskRead,
    responses={
        200: {"description": "Task completion status toggled", "model": TaskRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot modify other users' tasks", "model": ErrorResponse},
        404: {"description": "Task not found", "model": ErrorResponse},
    },
    summary="Toggle task completion",
    description="Toggle task completion status. pending → completed (sets completed_at), completed → pending (clears completed_at).",
)
async def toggle_task_completion(
    user_id: str,
    task_id: UUID,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Toggle task completion status.

    pending → completed: sets completed_at
    completed → pending: clears completed_at
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.TASK_NOT_FOUND, "Task not found")
        )

    # Toggle status
    if task.status == TaskStatus.COMPLETE:
        task.status = TaskStatus.PENDING
        task.completed_at = None
    else:
        task.status = TaskStatus.COMPLETE
        task.completed_at = datetime.utcnow()

    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)
