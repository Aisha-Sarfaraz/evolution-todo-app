"""Category SQLModel - Task organization by category."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlmodel import Field, SQLModel, Column


class Category(SQLModel, table=True):
    """Category entity for task classification."""

    __tablename__ = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: Optional[str] = Field(default=None, sa_column=Column(sa.VARCHAR(64), nullable=True, index=True))
    name: str = Field(max_length=100, nullable=False)
    is_system: bool = Field(default=False, nullable=False, index=True)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


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
