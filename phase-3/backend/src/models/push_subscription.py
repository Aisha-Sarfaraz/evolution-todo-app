"""T081: PushSubscription SQLModel.

Stores browser push notification subscription endpoints and keys.
Maps to the 'push_subscriptions' table created by Alembic migration 013.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Column, Field, SQLModel


class PushSubscription(SQLModel, table=True):
    """A browser push notification subscription.

    Attributes:
        id: Unique subscription identifier (UUID4).
        user_id: FK to users.id.
        endpoint: Push service endpoint URL (unique).
        keys: JSONB with p256dh and auth keys.
        device_info: Optional device metadata.
        created_at: When this subscription was created.
    """

    __tablename__ = "push_subscriptions"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: str = Field(
        sa_column=sa.Column(sa.VARCHAR(64), nullable=False, index=True)
    )
    endpoint: str = Field(
        sa_column=sa.Column(sa.VARCHAR(500), nullable=False, unique=True)
    )
    keys: dict[str, Any] = Field(
        sa_column=Column(sa.JSON, nullable=False)
    )
    device_info: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(sa.JSON, nullable=True),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
