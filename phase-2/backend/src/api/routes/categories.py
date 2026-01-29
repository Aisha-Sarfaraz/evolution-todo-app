"""Category management API routes.

T093-T095: Category CRUD endpoints with user isolation.

Endpoints:
- GET /api/{user_id}/categories - List categories (system + user's custom)
- POST /api/{user_id}/categories - Create custom category
- DELETE /api/{user_id}/categories/{id} - Delete custom category

@see specs/001-fullstack-todo-web/spec.md - FR-057, FR-058, FR-059
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ValidatedUser
from src.database import get_session
from src.models.category import Category
from src.models.task import Task
from src.utils.errors import ErrorCode, ErrorResponse, format_error


router = APIRouter(prefix="/api/{user_id}/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str | None = Field(None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryRead(BaseModel):
    """Schema for reading a category."""
    id: UUID
    name: str
    is_system: bool
    color: str | None
    user_id: str | None

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """Response schema for category list."""
    categories: list[CategoryRead]
    total: int


@router.get(
    "",
    response_model=CategoryListResponse,
    responses={
        200: {"description": "Categories retrieved successfully", "model": CategoryListResponse},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot access other users' categories", "model": ErrorResponse},
    },
    summary="List categories",
    description="List all categories available to the user. Includes system categories "
                "(Work, Personal, Shopping, Health, Fitness, Finance, Education, Home) and user's custom categories.",
)
async def list_categories(
    user_id: str,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """List all categories available to the user.

    Returns system categories (available to all) and user's custom categories.
    System categories: Work, Personal, Shopping, Health, Fitness, Finance, Education, Home.
    """
    # Get system categories + user's custom categories
    query = select(Category).where(
        (Category.is_system == True) | (Category.user_id == user_id)
    ).order_by(Category.is_system.desc(), Category.name.asc())

    result = await session.execute(query)
    categories = result.scalars().all()

    return CategoryListResponse(
        categories=[CategoryRead.model_validate(cat) for cat in categories],
        total=len(categories),
    )


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Category created successfully", "model": CategoryRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot create categories for other users", "model": ErrorResponse},
        409: {"description": "Category with this name already exists", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    summary="Create category",
    description="Create a new custom category. Name must be unique per user (case-insensitive). "
                "Optional color in hex format (#RRGGBB).",
)
async def create_category(
    user_id: str,
    category_data: CategoryCreate,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Create a new custom category.

    Validates name uniqueness per user (case-insensitive).
    User cannot create system categories.
    """
    # Check for duplicate name (case-insensitive)
    existing = await session.execute(
        select(Category).where(
            (Category.user_id == user_id) &
            (func.lower(Category.name) == func.lower(category_data.name))
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=format_error(
                ErrorCode.DUPLICATE_CATEGORY,
                f"Category '{category_data.name}' already exists"
            )
        )

    # Create custom category
    category = Category(
        user_id=user_id,
        name=category_data.name.strip(),
        color=category_data.color,
        is_system=False,
    )

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return CategoryRead.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Category deleted successfully"},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot delete system categories or other users' categories", "model": ErrorResponse},
        404: {"description": "Category not found", "model": ErrorResponse},
    },
    summary="Delete category",
    description="Delete a custom category. Cannot delete system categories. "
                "Tasks using this category will have their category_id set to null.",
)
async def delete_category(
    user_id: str,
    category_id: UUID,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Delete a custom category.

    Cannot delete system categories.
    Tasks using this category will have category_id set to null.
    """
    # Get category
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.CATEGORY_NOT_FOUND, "Category not found")
        )

    # Cannot delete system categories
    if category.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=format_error(ErrorCode.FORBIDDEN, "Cannot delete system categories")
        )

    # Can only delete own custom categories
    if category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=format_error(ErrorCode.FORBIDDEN, "Cannot delete other users' categories")
        )

    # Set category_id to null for all tasks using this category
    await session.execute(
        update(Task).where(Task.category_id == category_id).values(category_id=None)
    )

    # Delete category
    await session.delete(category)
    await session.commit()

    return None
