"""Unit tests for Task model validation.

T058: [US2] Unit test for Task model validation
Tests title, description, status, and priority validation.
"""

import pytest
from uuid import uuid4


class TestTaskModelValidation:
    """Tests for Task model field validation."""

    def test_task_title_non_empty_required(self):
        """Test that task title cannot be empty."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="", user_id=uuid4())

        errors = exc_info.value.errors()
        assert any("title" in str(e).lower() for e in errors)

    def test_task_title_max_200_chars(self):
        """Test that task title is limited to 200 characters."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        # 200 chars should be valid
        valid_title = "a" * 200
        task = TaskCreate(title=valid_title, user_id=uuid4())
        assert len(task.title) == 200

        # 201 chars should fail
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="a" * 201, user_id=uuid4())

        errors = exc_info.value.errors()
        assert any("title" in str(e).lower() for e in errors)

    def test_task_description_truncation_at_2000_chars(self):
        """Test that task description is truncated at 2000 characters."""
        from src.models.task import TaskCreate

        long_description = "a" * 2500
        task = TaskCreate(
            title="Test Task",
            user_id=uuid4(),
            description=long_description
        )

        # Should be truncated to 2000
        assert len(task.description) == 2000

    def test_task_status_enum_validation(self):
        """Test that task status must be valid enum value."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate, TaskStatus

        # Valid statuses should work
        for status in TaskStatus:
            task = TaskCreate(
                title="Test",
                user_id=uuid4(),
                status=status
            )
            assert task.status == status

    def test_task_status_invalid_value_fails(self):
        """Test that invalid status value fails validation."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        with pytest.raises(ValidationError):
            TaskCreate(
                title="Test",
                user_id=uuid4(),
                status="invalid_status"
            )

    def test_task_priority_enum_validation(self):
        """Test that task priority must be valid enum value."""
        from src.models.task import TaskCreate, TaskPriority

        # Valid priorities should work
        for priority in TaskPriority:
            task = TaskCreate(
                title="Test",
                user_id=uuid4(),
                priority=priority
            )
            assert task.priority == priority

    def test_task_priority_invalid_value_fails(self):
        """Test that invalid priority value fails validation."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        with pytest.raises(ValidationError):
            TaskCreate(
                title="Test",
                user_id=uuid4(),
                priority="invalid_priority"
            )

    def test_task_default_status_is_pending(self):
        """Test that default status is pending."""
        from src.models.task import TaskCreate, TaskStatus

        task = TaskCreate(title="Test", user_id=uuid4())
        assert task.status == TaskStatus.PENDING

    def test_task_default_priority_is_medium(self):
        """Test that default priority is medium."""
        from src.models.task import TaskCreate, TaskPriority

        task = TaskCreate(title="Test", user_id=uuid4())
        assert task.priority == TaskPriority.MEDIUM

    def test_task_description_optional(self):
        """Test that description is optional."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="Test", user_id=uuid4())
        assert task.description is None

    def test_task_category_id_optional(self):
        """Test that category_id is optional."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="Test", user_id=uuid4())
        assert task.category_id is None

    def test_task_title_whitespace_trimmed(self):
        """Test that title whitespace is trimmed."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="  Test Task  ", user_id=uuid4())
        assert task.title == "Test Task"
