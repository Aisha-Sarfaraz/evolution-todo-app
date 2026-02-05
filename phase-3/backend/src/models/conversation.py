"""T018: Conversation SQLModel.

Represents a chat conversation belonging to a user.
Maps to the 'conversations' table created by Alembic migration 009.
"""

from datetime import datetime, timezone, UTC
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """A chat conversation between a user and the AI assistant.

    Attributes:
        id: Unique conversation identifier (UUID4).
        user_id: Owner user ID (FK to users.id).
        title: Auto-generated from first message, nullable initially.
        created_at: When the conversation started.
        updated_at: Last activity timestamp.
    """

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: str = Field(
        sa_column=sa.Column(sa.VARCHAR(64), nullable=False, index=True)
    )
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )


class ConversationRead(SQLModel):
    """Schema for conversation list responses."""

    id: UUID
    title: Optional[str]
    last_message_preview: Optional[str] = None
    updated_at: datetime


class ConversationCreate(SQLModel):
    """Schema for creating a conversation."""

    user_id: str
    title: Optional[str] = None
