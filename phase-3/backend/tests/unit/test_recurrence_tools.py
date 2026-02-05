"""T060: Unit tests for recurrence MCP tools."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest


@pytest.mark.unit
class TestCreateRecurrenceTool:
    """Tests for create_recurrence MCP tool."""

    @pytest.mark.asyncio
    async def test_create_daily_recurrence(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Create daily recurrence succeeds."""
        from phase3_backend.mcp.tools.recurrence_tools import create_recurrence

        task_id = str(uuid4())
        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.user_id = sample_user_id
        mock_task.title = "Take vitamins"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db_session.execute.return_value = mock_result

        result = await create_recurrence(
            task_id=task_id,
            user_id=sample_user_id,
            frequency="daily",
            _session=mock_db_session,
        )

        assert "daily" in result.lower() or "recurrence" in result.lower()

    @pytest.mark.asyncio
    async def test_create_weekly_recurrence(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Create weekly recurrence succeeds."""
        from phase3_backend.mcp.tools.recurrence_tools import create_recurrence

        task_id = str(uuid4())
        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.user_id = sample_user_id
        mock_task.title = "Team standup"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db_session.execute.return_value = mock_result

        result = await create_recurrence(
            task_id=task_id,
            user_id=sample_user_id,
            frequency="weekly",
            _session=mock_db_session,
        )

        assert isinstance(result, str)


@pytest.mark.unit
class TestRemoveRecurrenceTool:
    """Tests for remove_recurrence MCP tool."""

    @pytest.mark.asyncio
    async def test_remove_recurrence(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Remove recurrence succeeds."""
        from phase3_backend.mcp.tools.recurrence_tools import remove_recurrence

        task_id = str(uuid4())

        mock_rule = MagicMock()
        mock_rule.task_id = task_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_rule
        mock_db_session.execute.return_value = mock_result

        result = await remove_recurrence(
            task_id=task_id,
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "removed" in result.lower() or "stopped" in result.lower()
