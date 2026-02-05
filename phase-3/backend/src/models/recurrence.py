"""T064: RecurrenceRule SQLModel.

Represents a recurrence rule attached to a task.
Maps to the 'recurrence_rules' table created by Alembic migration 011.
"""

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Column, Field, SQLModel


class RecurrenceRule(SQLModel, table=True):
    """A recurrence rule for automatically creating new task instances.

    Attributes:
        id: Unique rule identifier (UUID4).
        task_id: FK to tasks.id (UNIQUE, CASCADE delete).
        frequency: daily, weekly, monthly, or yearly.
        interval: How often (e.g., 2 = every 2 weeks).
        days_of_week: Array of weekday integers (0=Mon, 6=Sun) for weekly.
        day_of_month: Specific day of month for monthly.
        end_date: Stop creating instances after this date.
        next_occurrence: When the next task instance should be created.
        created_at: When this rule was created.
    """

    __tablename__ = "recurrence_rules"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    task_id: UUID = Field(
        sa_column=sa.Column(
            sa.Uuid,
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    frequency: str = Field(
        sa_column=sa.Column(
            sa.VARCHAR(20),
            sa.CheckConstraint("frequency IN ('daily','weekly','monthly','yearly')"),
            nullable=False,
        )
    )
    interval: int = Field(default=1, ge=1)
    days_of_week: Optional[list[int]] = Field(
        default=None,
        sa_column=Column(ARRAY(sa.INTEGER), nullable=True),
    )
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    end_date: Optional[date] = Field(default=None)
    next_occurrence: datetime = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
