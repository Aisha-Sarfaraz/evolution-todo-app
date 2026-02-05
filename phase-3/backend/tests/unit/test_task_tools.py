"""T022-T024: Unit tests for MCP task CRUD tools.

Tests create_task, list_tasks, update_task, complete_task, and delete_task
MCP tools with input validation, user isolation, and error handling.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest


@pytest.mark.unit
class TestCreateTaskTool:
    """T022: Tests for create_task MCP tool."""

    @pytest.mark.asyncio
    async def test_create_task_valid_input(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Create task with valid title returns success."""
        from phase3_backend.mcp.tools.task_tools import create_task

        result = await create_task(
            title="Buy groceries",
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "Buy groceries" in result
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_task_with_description_and_priority(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Create task with optional description and priority."""
        from phase3_backend.mcp.tools.task_tools import create_task

        result = await create_task(
            title="Important meeting",
            description="Discuss Q1 roadmap",
            priority="High",
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "Important meeting" in result

    @pytest.mark.asyncio
    async def test_create_task_empty_title_rejected(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Empty title raises validation error."""
        from phase3_backend.mcp.tools.task_tools import create_task

        result = await create_task(
            title="",
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "error" in result.lower() or "empty" in result.lower()

    @pytest.mark.asyncio
    async def test_create_task_whitespace_title_rejected(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Whitespace-only title raises validation error."""
        from phase3_backend.mcp.tools.task_tools import create_task

        result = await create_task(
            title="   ",
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "error" in result.lower() or "empty" in result.lower()


@pytest.mark.unit
class TestListTasksTool:
    """T023: Tests for list_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_returns_user_tasks(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """List tasks returns only the requesting user's tasks."""
        from phase3_backend.mcp.tools.task_tools import list_tasks

        # Mock query result
        mock_task = MagicMock()
        mock_task.title = "Test task"
        mock_task.status = "pending"
        mock_task.priority = "Medium"
        mock_task.id = uuid4()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_task]
        mock_db_session.execute.return_value = mock_result

        result = await list_tasks(
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "Test task" in result

    @pytest.mark.asyncio
    async def test_list_tasks_with_status_filter(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """List tasks with status filter applies filter."""
        from phase3_backend.mcp.tools.task_tools import list_tasks

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await list_tasks(
            user_id=sample_user_id,
            status="pending",
            _session=mock_db_session,
        )

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_list_tasks_with_priority_filter(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """List tasks with priority filter applies filter."""
        from phase3_backend.mcp.tools.task_tools import list_tasks

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await list_tasks(
            user_id=sample_user_id,
            priority="High",
            _session=mock_db_session,
        )

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_list_tasks_empty_returns_message(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """List tasks with no results returns helpful message."""
        from phase3_backend.mcp.tools.task_tools import list_tasks

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await list_tasks(
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "no task" in result.lower() or "empty" in result.lower() or "0" in result


@pytest.mark.unit
class TestUpdateDeleteTaskTools:
    """T024: Tests for update_task, complete_task, delete_task MCP tools."""

    @pytest.mark.asyncio
    async def test_update_task_title(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Update task title succeeds."""
        from phase3_backend.mcp.tools.task_tools import update_task

        task_id = str(uuid4())
        mock_task = MagicMock()
        mock_task.title = "Old title"
        mock_task.user_id = sample_user_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db_session.execute.return_value = mock_result

        result = await update_task(
            task_id=task_id,
            user_id=sample_user_id,
            title="New title",
            _session=mock_db_session,
        )

        assert "updated" in result.lower() or "New title" in result

    @pytest.mark.asyncio
    async def test_complete_task(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Complete task sets status to complete."""
        from phase3_backend.mcp.tools.task_tools import complete_task

        task_id = str(uuid4())
        mock_task = MagicMock()
        mock_task.title = "Test task"
        mock_task.user_id = sample_user_id
        mock_task.status = "pending"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db_session.execute.return_value = mock_result

        result = await complete_task(
            task_id=task_id,
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "complete" in result.lower() or "done" in result.lower()

    @pytest.mark.asyncio
    async def test_delete_task(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Delete task performs hard delete."""
        from phase3_backend.mcp.tools.task_tools import delete_task

        task_id = str(uuid4())
        mock_task = MagicMock()
        mock_task.title = "Task to delete"
        mock_task.user_id = sample_user_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db_session.execute.return_value = mock_result

        result = await delete_task(
            task_id=task_id,
            user_id=sample_user_id,
            _session=mock_db_session,
        )

        assert "delete" in result.lower()

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(self, mock_db_session: AsyncMock, sample_user_id: str) -> None:
        """Update non-existent task returns error."""
        from phase3_backend.mcp.tools.task_tools import update_task

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await update_task(
            task_id=str(uuid4()),
            user_id=sample_user_id,
            title="New title",
            _session=mock_db_session,
        )

        assert "not found" in result.lower() or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_user_isolation_on_update(self, mock_db_session: AsyncMock) -> None:
        """Cannot update another user's task."""
        from phase3_backend.mcp.tools.task_tools import update_task

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Not found due to user_id filter
        mock_db_session.execute.return_value = mock_result

        result = await update_task(
            task_id=str(uuid4()),
            user_id="different-user",
            title="Hacked title",
            _session=mock_db_session,
        )

        assert "not found" in result.lower() or "error" in result.lower()
