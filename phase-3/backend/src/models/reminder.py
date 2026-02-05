"""T080: ReminderMetadata SQLModel.

Stores due dates, reminder times, and notification status for tasks.
Maps to the 'reminder_metadata' table created by Alembic migration 012.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class ReminderMetadata(SQLModel, table=True):
    """Reminder metadata attached to a task.

    Attributes:
        id: Unique reminder identifier (UUID4).
        task_id: FK to tasks.id (UNIQUE, CASCADE delete).
        due_date: When the task is due.
        reminder_time: When to send the notification.
        notification_sent: Whether the notification has been delivered.
        snooze_until: Snoozed until this time.
        created_at: When this reminder was created.
    """

    __tablename__ = "reminder_metadata"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    task_id: UUID = Field(
        sa_column=sa.Column(
            sa.Uuid,
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    due_date: Optional[datetime] = Field(default=None)
    reminder_time: Optional[datetime] = Field(default=None)
    notification_sent: bool = Field(default=False)
    snooze_until: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
