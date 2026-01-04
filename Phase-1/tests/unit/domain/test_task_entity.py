"""
Unit tests for Task entity creation and validation.

Tests cover:
- T007: Task entity creation with valid inputs
- T008: Task title validation (empty, length, trim)
- T009: Task description validation (truncation)

TDD Phase: RED - These tests MUST FAIL before implementation
"""

import pytest
from datetime import datetime
from src.domain.task import Task
from src.domain.exceptions import DomainValidationError


class TestTaskEntityCreation:
    """Test Task entity creation with valid inputs (T007)"""

    def test_task_creation_with_title_only(self):
        """Task creates successfully with title only, description defaults to empty string"""
        task = Task(title="Buy groceries")

        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.status == "pending"
        assert task.completed_at is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_creation_with_title_and_description(self):
        """Task creates successfully with both title and description"""
        task = Task(title="Buy groceries", description="Milk, eggs, bread")

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.status == "pending"

    def test_task_id_is_uuid4_string(self):
        """Task ID is auto-generated as UUID4 string"""
        task = Task(title="Test task")

        assert isinstance(task.id, str)
        assert len(task.id) == 36  # UUID4 format: 8-4-4-4-12 chars with hyphens
        assert task.id.count("-") == 4

    def test_status_defaults_to_pending(self):
        """Task status defaults to 'pending' on creation"""
        task = Task(title="Test task")

        assert task.status == "pending"


class TestTaskTitleValidation:
    """Test Task title validation rules (T008)"""

    def test_empty_title_raises_validation_error(self):
        """Empty title (after trim) raises DomainValidationError"""
        with pytest.raises(DomainValidationError, match="Title cannot be empty"):
            Task(title="")

    def test_whitespace_only_title_raises_validation_error(self):
        """Whitespace-only title (after trim) raises DomainValidationError"""
        with pytest.raises(DomainValidationError, match="Title cannot be empty"):
            Task(title="   ")

    def test_title_exceeding_200_chars_raises_validation_error(self):
        """Title > 200 chars raises DomainValidationError"""
        long_title = "A" * 201

        with pytest.raises(DomainValidationError, match="Title cannot exceed 200 characters"):
            Task(title=long_title)

    def test_title_exactly_200_chars_succeeds(self):
        """Title with exactly 200 chars is valid"""
        title_200 = "A" * 200
        task = Task(title=title_200)

        assert task.title == title_200
        assert len(task.title) == 200

    def test_title_leading_trailing_whitespace_trimmed(self):
        """Leading and trailing whitespace is automatically trimmed"""
        task = Task(title="  Buy groceries  ")

        assert task.title == "Buy groceries"
        assert task.title == task.title.strip()


class TestTaskDescriptionValidation:
    """Test Task description validation rules (T009)"""

    def test_description_with_2000_chars_accepted(self):
        """Description with exactly 2000 chars is accepted"""
        desc_2000 = "A" * 2000
        task = Task(title="Test", description=desc_2000)

        assert task.description == desc_2000
        assert len(task.description) == 2000

    def test_description_exceeding_2000_chars_auto_truncated(self):
        """Description > 2000 chars is auto-truncated to 2000 chars"""
        desc_2001 = "A" * 2001
        task = Task(title="Test", description=desc_2001)

        assert len(task.description) == 2000
        assert task.description == desc_2001[:2000]

    def test_description_truncation_logs_warning(self, caplog):
        """Description truncation logs a warning message"""
        desc_3000 = "A" * 3000

        with caplog.at_level("WARNING"):
            task = Task(title="Test", description=desc_3000)

        # Verify warning was logged
        assert "Description truncated" in caplog.text or "truncated to 2000 characters" in caplog.text
