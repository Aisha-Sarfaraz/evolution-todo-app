"""Tag management API routes.

T096-T098: Tag CRUD endpoints with user isolation.

Endpoints:
- GET /api/{user_id}/tags - List user's tags
- POST /api/{user_id}/tags - Create tag
- PUT /api/{user_id}/tags/{id} - Rename tag
- DELETE /api/{user_id}/tags/{id} - Delete tag

@see specs/001-fullstack-todo-web/spec.md - FR-060, FR-061, FR-062, FR-063
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ValidatedUser
from src.database import get_session
from src.models.tag import Tag
from src.models.task_tag import TaskTag
from src.utils.errors import ErrorCode, ErrorResponse, format_error


router = APIRouter(prefix="/api/{user_id}/tags", tags=["tags"])


class TagCreate(BaseModel):
    """Schema for creating a tag."""
    name: str = Field(..., min_length=1, max_length=50)


class TagUpdate(BaseModel):
    """Schema for updating a tag."""
    name: str = Field(..., min_length=1, max_length=50)


class TagRead(BaseModel):
    """Schema for reading a tag."""
    id: UUID
    name: str
    user_id: str

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    """Response schema for tag list."""
    tags: list[TagRead]
    total: int


@router.get(
    "",
    response_model=TagListResponse,
    responses={
        200: {"description": "Tags retrieved successfully", "model": TagListResponse},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot access other users' tags", "model": ErrorResponse},
    },
    summary="List tags",
    description="List all tags for the authenticated user, sorted alphabetically by name.",
)
async def list_tags(
    user_id: str,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """List all tags for the authenticated user.

    Returns tags sorted alphabetically by name.
    """
    query = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name.asc())

    result = await session.execute(query)
    tags = result.scalars().all()

    return TagListResponse(
        tags=[TagRead.model_validate(tag) for tag in tags],
        total=len(tags),
    )


@router.post(
    "",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Tag created successfully", "model": TagRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot create tags for other users", "model": ErrorResponse},
        409: {"description": "Tag with this name already exists", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    summary="Create tag",
    description="Create a new tag. Name must be unique per user (case-insensitive). "
                "Max 50 characters. Whitespace is trimmed.",
)
async def create_tag(
    user_id: str,
    tag_data: TagCreate,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Create a new tag.

    Validates name uniqueness per user (case-insensitive).
    Trims whitespace from name.
    """
    name = tag_data.name.strip()

    # Check for duplicate name (case-insensitive)
    existing = await session.execute(
        select(Tag).where(
            (Tag.user_id == user_id) &
            (func.lower(Tag.name) == func.lower(name))
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=format_error(
                ErrorCode.DUPLICATE_TAG,
                f"Tag '{name}' already exists. Tags must be unique (case-insensitive)."
            )
        )

    # Create tag
    tag = Tag(
        user_id=user_id,
        name=name,
    )

    session.add(tag)
    await session.commit()
    await session.refresh(tag)

    return TagRead.model_validate(tag)


@router.put(
    "/{tag_id}",
    response_model=TagRead,
    responses={
        200: {"description": "Tag renamed successfully", "model": TagRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot rename other users' tags", "model": ErrorResponse},
        404: {"description": "Tag not found", "model": ErrorResponse},
        409: {"description": "Tag with this name already exists", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    summary="Rename tag",
    description="Rename an existing tag. New name must be unique per user (case-insensitive). "
                "All tasks with this tag are automatically updated.",
)
async def update_tag(
    user_id: str,
    tag_id: UUID,
    tag_data: TagUpdate,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Rename a tag.

    Updates tag name for all associated tasks (single source of truth).
    Validates new name uniqueness per user (case-insensitive).
    """
    # Get existing tag
    result = await session.execute(
        select(Tag).where((Tag.id == tag_id) & (Tag.user_id == user_id))
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.TAG_NOT_FOUND, "Tag not found")
        )

    new_name = tag_data.name.strip()

    # Check for duplicate name (case-insensitive, excluding current tag)
    existing = await session.execute(
        select(Tag).where(
            (Tag.user_id == user_id) &
            (Tag.id != tag_id) &
            (func.lower(Tag.name) == func.lower(new_name))
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=format_error(
                ErrorCode.DUPLICATE_TAG,
                f"Tag '{new_name}' already exists. Tags must be unique (case-insensitive)."
            )
        )

    # Update tag name
    tag.name = new_name
    await session.commit()
    await session.refresh(tag)

    return TagRead.model_validate(tag)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Tag deleted successfully"},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot delete other users' tags", "model": ErrorResponse},
        404: {"description": "Tag not found", "model": ErrorResponse},
    },
    summary="Delete tag",
    description="Delete a tag permanently. All task-tag associations are removed.",
)
async def delete_tag(
    user_id: str,
    tag_id: UUID,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Delete a tag.

    Removes all task-tag associations (CASCADE delete on TaskTag).
    Returns 404 for non-existent or cross-user access.
    """
    # Get tag
    result = await session.execute(
        select(Tag).where((Tag.id == tag_id) & (Tag.user_id == user_id))
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.TAG_NOT_FOUND, "Tag not found")
        )

    # Delete all task-tag associations first (if not using CASCADE)
    await session.execute(
        delete(TaskTag).where(TaskTag.tag_id == tag_id)
    )

    # Delete tag
    await session.delete(tag)
    await session.commit()

    return None
