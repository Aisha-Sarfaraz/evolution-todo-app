"""TaskTag SQLModel - Join table for many-to-many relationship between Tasks and Tags."""

from datetime import datetime
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship


class TaskTag(SQLModel, table=True):
    """TaskTag join table for task-tag many-to-many relationship.

    This table enables flexible task organization where:
    - One task can have multiple tags
    - One tag can be assigned to multiple tasks

    Attributes:
        task_id: Foreign key to tasks.id (CASCADE on delete)
        tag_id: Foreign key to tags.id (CASCADE on delete)
        created_at: Timestamp when tag was assigned to task

    Composite Primary Key:
        (task_id, tag_id) - Ensures no duplicate tag assignments

    Cascade Behavior:
        - Deleting a task removes all its TaskTag associations
        - Deleting a tag removes all its TaskTag associations
        - Both use ON DELETE CASCADE for automatic cleanup

    Business Rules:
        - A task-tag pair can only exist once (enforced by composite PK)
        - created_at tracks when the tag was assigned to the task
        - No direct modification - only create and delete operations
    """

    __tablename__ = "task_tag"

    task_id: UUID = Field(foreign_key="tasks.id", primary_key=True, nullable=False)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    # task: "Task" = Relationship(back_populates="task_tags")
    # tag: "Tag" = Relationship(back_populates="task_tags")


class TaskTagCreate(SQLModel):
    """Schema for assigning a tag to a task."""
    task_id: UUID
    tag_id: UUID


class TaskTagRead(SQLModel):
    """Schema for task-tag association responses."""
    task_id: UUID
    tag_id: UUID
    created_at: datetime
