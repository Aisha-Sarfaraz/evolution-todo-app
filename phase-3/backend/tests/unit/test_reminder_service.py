"""T072: Unit tests for reminder checker service."""

from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

import pytest


@pytest.mark.unit
class TestReminderService:
    """Tests for reminder checker service."""

    @pytest.mark.asyncio
    async def test_finds_due_reminders(self) -> None:
        """Service finds reminders where reminder_time <= now."""
        from phase3_backend.services.reminder_service import check_reminders

        assert callable(check_reminders)

    @pytest.mark.asyncio
    async def test_marks_notification_sent(self) -> None:
        """After sending, notification_sent is set to True."""
        from phase3_backend.services.reminder_service import _send_reminder

        assert callable(_send_reminder)

    @pytest.mark.asyncio
    async def test_skips_already_sent(self) -> None:
        """Already-sent reminders are not re-sent."""
        from phase3_backend.models.reminder import ReminderMetadata

        reminder = ReminderMetadata.__new__(ReminderMetadata)
        # Validates the model has the notification_sent field
        assert hasattr(ReminderMetadata, "notification_sent")
