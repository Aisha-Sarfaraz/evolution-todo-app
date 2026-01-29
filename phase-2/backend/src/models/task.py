"""Task SQLModel - Extended from Phase I with multi-user support and organization features."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlmodel import Field, SQLModel, Relationship, Column
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
    """Task entity - Extended from Phase I with multi-user support.

    Phase I Attributes (Preserved):
        id: Unique identifier (UUID4)
        title: Task title (1-200 characters, non-empty after trim)
        description: Task description (0-2000 characters, auto-truncated)
        status: Task status (pending | complete)
        created_at: Creation timestamp (immutable)
        updated_at: Last modification timestamp (auto-updated)
        completed_at: Completion timestamp (set when status changes to complete)

    Phase II New Attributes:
        user_id: Owner user ID (foreign key to users.id)
        priority: Task priority (Low | Medium | High | Urgent, default: Medium)
        category_id: Optional category assignment (foreign key to categories.id)

    Relationships:
        user: Owner user
        category: Optional assigned category
        task_tags: Many-to-many relationship to tags via TaskTag join table

    Business Rules (Phase I Invariants - Preserved):
        - Title must be non-empty after trimming whitespace
        - Title cannot exceed 200 characters
        - Description cannot exceed 2000 characters (auto-truncated if longer)
        - Status must be 'pending' or 'complete'
        - UUID4 used for IDs
        - Timestamps are immutable (except updated_at and completed_at)

    Phase II Invariants:
        - Priority must be one of: Low, Medium, High, Urgent
        - Tasks are user-scoped (user_id required, indexed for performance)
        - Category assignment is optional (category_id nullable)
        - Deleting a user cascades to all user tasks (ON DELETE CASCADE)
        - Deleting a category sets task.category_id to NULL (ON DELETE SET NULL)
    """

    __tablename__ = "tasks"

    # Phase I attributes (preserved)
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Phase II new attributes
    user_id: str = Field(sa_column=Column(sa.VARCHAR(64), nullable=False, index=True))
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False, index=True)
    category_id: Optional[UUID] = Field(default=None, foreign_key="categories.id", index=True)

    # Relationships
    # user: "User" = Relationship(back_populates="tasks")
    # category: Optional["Category"] = Relationship(back_populates="tasks")
    # task_tags: list["TaskTag"] = Relationship(back_populates="task")


class TaskCreate(SQLModel):
    """Schema for creating a task.

    Validation Rules:
        - Title must be non-empty after trimming whitespace
        - Title cannot exceed 200 characters
        - Description is truncated at 2000 characters if longer
    """
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    category_id: Optional[UUID] = None
    tag_ids: Optional[list[UUID]] = None  # Tag IDs to assign on creation
    user_id: Optional[str] = None  # Set by API endpoint from URL

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        """Override model_validate to apply validators."""
        from pydantic import ValidationError
        from pydantic_core import InitErrorDetails, PydanticCustomError

        if isinstance(obj, dict):
            # Apply title validation
            if "title" in obj:
                title = obj.get("title", "")
                if isinstance(title, str):
                    title = title.strip()
                    if not title:
                        raise ValidationError.from_exception_data(
                            "TaskCreate",
                            [
                                InitErrorDetails(
                                    type=PydanticCustomError('value_error', 'Title cannot be empty'),
                                    loc=('title',),
                                    input=obj.get("title"),
                                )
                            ],
                        )
                    if len(title) > 200:
                        raise ValidationError.from_exception_data(
                            "TaskCreate",
                            [
                                InitErrorDetails(
                                    type=PydanticCustomError('value_error', 'Title cannot exceed 200 characters'),
                                    loc=('title',),
                                    input=obj.get("title"),
                                )
                            ],
                        )
                    obj["title"] = title

            # Apply description truncation
            if "description" in obj and obj["description"] is not None:
                desc = obj["description"]
                if isinstance(desc, str) and len(desc) > 2000:
                    obj["description"] = desc[:2000]

        return super().model_validate(obj, *args, **kwargs)

    def __init__(self, **data):
        from pydantic import ValidationError
        from pydantic_core import InitErrorDetails, PydanticCustomError

        # Validate and transform title
        if "title" in data:
            title = data.get("title", "")
            if isinstance(title, str):
                title = title.strip()
                if not title:
                    raise ValidationError.from_exception_data(
                        "TaskCreate",
                        [
                            InitErrorDetails(
                                type=PydanticCustomError('value_error', 'Title cannot be empty'),
                                loc=('title',),
                                input=data.get("title"),
                            )
                        ],
                    )
                if len(title) > 200:
                    raise ValidationError.from_exception_data(
                        "TaskCreate",
                        [
                            InitErrorDetails(
                                type=PydanticCustomError('value_error', 'Title cannot exceed 200 characters'),
                                loc=('title',),
                                input=data.get("title"),
                            )
                        ],
                    )
                data["title"] = title

        # Truncate description if too long
        if "description" in data and data["description"] is not None:
            desc = data["description"]
            if isinstance(desc, str) and len(desc) > 2000:
                data["description"] = desc[:2000]

        super().__init__(**data)


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


class TaskUpdate(SQLModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[UUID] = None
    tag_ids: Optional[list[UUID]] = None  # List of tag IDs to assign


class TaskComplete(SQLModel):
    """Schema for toggling task completion status."""
    status: TaskStatus
