"""Category SQLModel - Task organization by category."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlmodel import Field, SQLModel, Relationship, Column


class Category(SQLModel, table=True):
    """Category entity for task classification.

    Supports both system-defined categories (is_system=True, user_id=NULL)
    and user-created custom categories (is_system=False, user_id=<user_uuid>).

    System categories:
    - Work, Personal, Shopping, Health, Fitness, Finance, Education, Home
    - Cannot be deleted by users
    - Visible to all users

    Attributes:
        id: Unique identifier (UUID4)
        user_id: Owner user ID (NULL for system categories)
        name: Category name (unique per user, case-insensitive)
        is_system: System category flag (default: False)
        color: Hex color code for UI display (e.g., "#3B82F6")
        created_at: Creation timestamp (immutable)

    Relationships:
        user: Owner user (NULL for system categories)
        tasks: All tasks assigned to this category
    """

    __tablename__ = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: Optional[str] = Field(default=None, sa_column=Column(sa.VARCHAR(64), nullable=True, index=True))
    name: str = Field(max_length=100, nullable=False)
    is_system: bool = Field(default=False, nullable=False, index=True)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    # user: Optional["User"] = Relationship(back_populates="categories")
    # tasks: list["Task"] = Relationship(back_populates="category")


class CategoryCreate(SQLModel):
    """Schema for creating a custom category."""
    name: str
    color: Optional[str] = None


class CategoryRead(SQLModel):
    """Schema for category responses."""
    id: UUID
    user_id: Optional[str]
    name: str
    is_system: bool
    color: Optional[str]
    created_at: datetime


class CategoryUpdate(SQLModel):
    """Schema for updating a category."""
    name: Optional[str] = None
    color: Optional[str] = None
