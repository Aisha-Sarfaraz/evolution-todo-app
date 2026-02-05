"""T019: Message SQLModel.

Represents a single message in a conversation (user or assistant role).
Maps to the 'messages' table created by Alembic migration 010.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Column, Field, SQLModel


class Message(SQLModel, table=True):
    """A single message in a chat conversation.

    Attributes:
        id: Unique message identifier (UUID4).
        conversation_id: FK to conversations.id (CASCADE delete).
        user_id: The user who owns this conversation.
        role: Either 'user' or 'assistant'.
        content: Message text content.
        tool_calls: Optional JSONB storing tool invocations and results.
        created_at: When the message was sent.
    """

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    conversation_id: UUID = Field(
        sa_column=sa.Column(
            sa.Uuid,
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    user_id: str = Field(
        sa_column=sa.Column(sa.VARCHAR(64), nullable=False, index=True)
    )
    role: str = Field(
        sa_column=sa.Column(
            sa.VARCHAR(20),
            sa.CheckConstraint("role IN ('user', 'assistant')"),
            nullable=False,
        )
    )
    content: str = Field(sa_column=sa.Column(sa.Text, nullable=False))
    tool_calls: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=sa.Column(sa.JSON, nullable=True),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )


class MessageRead(SQLModel):
    """Schema for message responses."""

    id: UUID
    role: str
    content: str
    tool_calls: Optional[dict[str, Any]] = None
    created_at: datetime


class MessageCreate(SQLModel):
    """Schema for creating a message."""

    conversation_id: UUID
    user_id: str
    role: str
    content: str
    tool_calls: Optional[dict[str, Any]] = None
