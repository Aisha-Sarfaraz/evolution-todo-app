"""
Unit tests for Task lifecycle methods.

Tests cover:
- T010: Task lifecycle methods (update_title, update_description, mark_complete)

TDD Phase: RED - These tests MUST FAIL before implementation
"""

import pytest
from datetime import datetime
from time import sleep
from src.domain.task import Task
from src.domain.exceptions import DomainValidationError, DomainStateError


class TestTaskUpdateTitle:
    """Test Task.update_title() method"""

    def test_update_title_with_valid_title(self):
        """update_title() with valid title updates title and updated_at"""
        task = Task(title="Old title")
        original_updated_at = task.updated_at
        sleep(0.001)  # Ensure timestamp difference

        task.update_title("New title")

        assert task.title == "New title"
        assert task.updated_at > original_updated_at

    def test_update_title_with_empty_title_raises_error(self):
        """update_title() with empty title raises DomainValidationError"""
        task = Task(title="Original title")

        with pytest.raises(DomainValidationError, match="Title cannot be empty"):
            task.update_title("")

    def test_update_title_with_title_exceeding_200_chars_raises_error(self):
        """update_title() with title > 200 chars raises DomainValidationError"""
        task = Task(title="Original title")
        long_title = "A" * 201

        with pytest.raises(DomainValidationError, match="Title cannot exceed 200 characters"):
            task.update_title(long_title)


class TestTaskUpdateDescription:
    """Test Task.update_description() method"""

    def test_update_description_updates_description_and_timestamp(self):
        """update_description() updates description and updated_at"""
        task = Task(title="Test", description="Old description")
        original_updated_at = task.updated_at
        sleep(0.001)  # Ensure timestamp difference

        task.update_description("New description")

        assert task.description == "New description"
        assert task.updated_at > original_updated_at

    def test_update_description_truncates_at_2000_chars(self):
        """update_description() auto-truncates if > 2000 chars"""
        task = Task(title="Test")
        desc_3000 = "A" * 3000

        task.update_description(desc_3000)

        assert len(task.description) == 2000
        assert task.description == desc_3000[:2000]


class TestTaskMarkComplete:
    """Test Task.mark_complete() method"""

    def test_mark_complete_on_pending_task(self):
        """mark_complete() on pending task sets status='complete' and completed_at"""
        task = Task(title="Test task")
        assert task.status == "pending"
        assert task.completed_at is None

        task.mark_complete()

        assert task.status == "complete"
        assert isinstance(task.completed_at, datetime)
        assert task.completed_at is not None

    def test_mark_complete_on_complete_task_raises_error(self):
        """mark_complete() on complete task raises DomainStateError"""
        task = Task(title="Test task")
        task.mark_complete()

        with pytest.raises(DomainStateError, match="Task is already complete"):
            task.mark_complete()

    def test_completed_at_is_none_for_pending_task(self):
        """completed_at is None for pending task"""
        task = Task(title="Test task")

        assert task.status == "pending"
        assert task.completed_at is None

    def test_completed_at_immutable_after_set(self):
        """completed_at is immutable after being set (calling mark_complete twice fails)"""
        task = Task(title="Test task")
        task.mark_complete()
        original_completed_at = task.completed_at

        # Attempt to mark complete again should raise error
        with pytest.raises(DomainStateError):
            task.mark_complete()

        # Verify completed_at did not change
        assert task.completed_at == original_completed_at


class TestTaskUpdatedTimestamp:
    """Test updated_at timestamp behavior"""

    def test_updated_at_changes_on_title_update(self):
        """updated_at changes when title is updated"""
        task = Task(title="Original")
        original_updated_at = task.updated_at
        sleep(0.001)

        task.update_title("Updated")

        assert task.updated_at > original_updated_at

    def test_updated_at_changes_on_description_update(self):
        """updated_at changes when description is updated"""
        task = Task(title="Test")
        original_updated_at = task.updated_at
        sleep(0.001)

        task.update_description("New description")

        assert task.updated_at > original_updated_at
