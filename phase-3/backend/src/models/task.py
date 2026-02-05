"""Task SQLModel - Extended from Phase I with multi-user support and organization features."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlmodel import Field, SQLModel, Column
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    COMPLETE = "complete"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class Task(SQLModel, table=True):
    """Task entity - Extended from Phase I with multi-user support."""

    __tablename__ = "tasks"

    # Phase I attributes (preserved)
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)

    # Phase II new attributes
    user_id: str = Field(sa_column=Column(sa.VARCHAR(64), nullable=False, index=True))
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False, index=True)
    category_id: Optional[UUID] = Field(default=None, foreign_key="categories.id", index=True)


class TaskCreate(SQLModel):
    """Schema for creating a task."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    category_id: Optional[UUID] = None
    tag_ids: Optional[list[UUID]] = None
    user_id: Optional[str] = None


class TaskRead(SQLModel):
    """Schema for task responses."""
    id: UUID
    user_id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    category_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    due_date: Optional[datetime] = None


class TaskUpdate(SQLModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[UUID] = None
    tag_ids: Optional[list[UUID]] = None


class TaskComplete(SQLModel):
    """Schema for toggling task completion status."""
    status: TaskStatus
