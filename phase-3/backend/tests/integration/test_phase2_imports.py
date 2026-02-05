"""T011: Integration tests for Phase II import compatibility.

Tests that Phase III can successfully import and use Phase II shared code:
database engine, auth dependencies, and Task model.
"""

import pytest


@pytest.mark.integration
class TestPhase2Imports:
    """Tests for Phase II code import compatibility."""

    def test_import_database_engine(self) -> None:
        """Verify Phase II database engine is importable."""
        from phase2_backend.database import engine, async_session_maker, get_session

        assert engine is not None
        assert async_session_maker is not None
        assert callable(get_session)

    def test_import_auth_dependencies(self) -> None:
        """Verify Phase II auth dependencies are importable."""
        from phase2_backend.api.dependencies import (
            get_current_user,
            validate_user_id_match,
            CurrentUser,
            ValidatedUser,
        )

        assert callable(get_current_user)
        assert callable(validate_user_id_match)
        assert CurrentUser is not None
        assert ValidatedUser is not None

    def test_import_task_model(self) -> None:
        """Verify Phase II Task model is importable with all fields."""
        from phase2_backend.models.task import (
            Task,
            TaskCreate,
            TaskRead,
            TaskUpdate,
            TaskStatus,
            TaskPriority,
        )

        assert hasattr(Task, "id")
        assert hasattr(Task, "user_id")
        assert hasattr(Task, "title")
        assert hasattr(Task, "status")
        assert hasattr(Task, "priority")
        assert TaskStatus.PENDING == "pending"
        assert TaskPriority.MEDIUM == "Medium"

    def test_task_model_has_table_name(self) -> None:
        """Verify Task model maps to 'tasks' table."""
        from phase2_backend.models.task import Task

        assert Task.__tablename__ == "tasks"

    def test_current_user_model_fields(self) -> None:
        """Verify CurrentUser model has required fields."""
        from phase2_backend.api.dependencies import CurrentUser

        user = CurrentUser(user_id="test-123", email="test@example.com")
        assert user.user_id == "test-123"
        assert user.email == "test@example.com"
