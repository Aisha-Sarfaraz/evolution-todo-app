"""T071: Unit tests for set_due_date MCP tool."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest


@pytest.mark.unit
class TestSetDueDateTool:
    """Tests for set_due_date MCP tool."""

    @pytest.mark.asyncio
    async def test_set_due_date_valid(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Set due date with valid date succeeds."""
        from phase3_backend.mcp.tools.reminder_tools import set_due_date

        task_id = str(uuid4())
        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.user_id = sample_user_id
        mock_task.title = "Call dentist"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db_session.execute.return_value = mock_result

        result = await set_due_date(
            task_id=task_id,
            user_id=sample_user_id,
            due_date="2026-02-15T14:00:00Z",
            _session=mock_db_session,
        )

        assert "due" in result.lower() or "2026" in result

    @pytest.mark.asyncio
    async def test_set_due_date_with_reminder(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Set due date with reminder time."""
        from phase3_backend.mcp.tools.reminder_tools import set_due_date

        task_id = str(uuid4())
        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.user_id = sample_user_id
        mock_task.title = "Meeting prep"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db_session.execute.return_value = mock_result

        result = await set_due_date(
            task_id=task_id,
            user_id=sample_user_id,
            due_date="2026-02-15T14:00:00Z",
            reminder_time="2026-02-15T13:00:00Z",
            _session=mock_db_session,
        )

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_set_due_date_user_isolation(self, mock_db_session: AsyncMock) -> None:
        """Cannot set due date on another user's task."""
        from phase3_backend.mcp.tools.reminder_tools import set_due_date

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await set_due_date(
            task_id=str(uuid4()),
            user_id="wrong-user",
            due_date="2026-02-15T14:00:00Z",
            _session=mock_db_session,
        )

        assert "not found" in result.lower() or "error" in result.lower()
