"""Tag SQLModel - User-created tags for flexible task organization."""

from datetime import datetime
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlmodel import Field, SQLModel, Relationship, Column


class Tag(SQLModel, table=True):
    """Tag entity for flexible task organization.

    Tags are user-created labels that can be assigned to multiple tasks
    via the TaskTag join table (many-to-many relationship).

    Attributes:
        id: Unique identifier (UUID4)
        user_id: Owner user ID (tags are user-specific)
        name: Tag name (unique per user, case-insensitive, max 50 chars)
        created_at: Creation timestamp (immutable)

    Relationships:
        user: Owner user
        task_tags: All TaskTag associations (join table entries)

    Business Rules:
        - Tag names must be unique per user (case-insensitive)
        - Tag names are trimmed of whitespace
        - Deleting a tag removes all TaskTag associations (CASCADE)
        - Renaming a tag updates all associated tasks automatically
    """

    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: str = Field(sa_column=Column(sa.VARCHAR(64), nullable=False, index=True))
    name: str = Field(max_length=50, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    # user: "User" = Relationship(back_populates="tags")
    # task_tags: list["TaskTag"] = Relationship(back_populates="tag")


class TagCreate(SQLModel):
    """Schema for creating a tag."""
    name: str  # Will be trimmed and validated for uniqueness (case-insensitive)


class TagRead(SQLModel):
    """Schema for tag responses."""
    id: UUID
    user_id: str
    name: str
    created_at: datetime


class TagUpdate(SQLModel):
    """Schema for renaming a tag."""
    name: str  # New tag name (validated for uniqueness)
