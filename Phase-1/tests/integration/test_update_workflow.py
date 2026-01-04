"""
Integration tests for Update Task workflow (User Story 3).

Tests cover:
- T051-T058: Update task integration tests

User Story P3: User wants to edit task title or description
"""

import pytest
from src.domain.task import Task
from src.storage.memory_repository import MemoryRepository
from src.cli.operations import update_task_operation


class TestUpdateTitleOnly:
    """Test update title only (T051 - P3.1)"""

    def test_update_title_only(self, monkeypatch, capsys):
        """Update title only, keep description unchanged"""
        repo = MemoryRepository()
        task = Task(title="Old title", description="Original description")
        repo.add(task)

        # Mock inputs: task_id, new_title, empty (keep description)
        inputs = iter([task.id[:8], "New title", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        update_task_operation(repo)

        # Verify title updated, description unchanged
        updated_task = repo.get(task.id)
        assert updated_task.title == "New title"
        assert updated_task.description == "Original description"


class TestUpdateDescriptionOnly:
    """Test update description only (T052 - P3.2)"""

    def test_update_description_only(self, monkeypatch, capsys):
        """Update description only, keep title unchanged"""
        repo = MemoryRepository()
        task = Task(title="Original title", description="Old description")
        repo.add(task)

        # Mock inputs: task_id, empty (keep title), new_description
        inputs = iter([task.id[:8], "", "New description"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        update_task_operation(repo)

        # Verify description updated, title unchanged
        updated_task = repo.get(task.id)
        assert updated_task.title == "Original title"
        assert updated_task.description == "New description"


class TestUpdateBothTitleAndDescription:
    """Test update both title and description (T053 - P3.3)"""

    def test_update_both_title_and_description(self, monkeypatch, capsys):
        """Update both title and description"""
        repo = MemoryRepository()
        task = Task(title="Old title", description="Old description")
        repo.add(task)

        # Mock inputs: task_id, new_title, new_description
        inputs = iter([task.id[:8], "New title", "New description"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        update_task_operation(repo)

        # Verify both updated
        updated_task = repo.get(task.id)
        assert updated_task.title == "New title"
        assert updated_task.description == "New description"


class TestUpdateWithEmptyTitleRejected:
    """Test update with empty title rejected (T054 - P3.4)"""

    def test_update_with_empty_title_shows_error(self, monkeypatch, capsys):
        """Update with empty title displays error"""
        repo = MemoryRepository()
        task = Task(title="Original title")
        repo.add(task)

        # Mock inputs: task_id, empty title (should fail)
        inputs = iter([task.id[:8], "", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        update_task_operation(repo)

        # Original title should remain (update failed due to empty new title being kept)
        updated_task = repo.get(task.id)
        assert updated_task.title == "Original title"


class TestUpdateWithInvalidTaskID:
    """Test update with invalid task ID (T055 - P3.5)"""

    def test_update_with_invalid_task_id_shows_error(self, monkeypatch, capsys):
        """Update with invalid task ID displays 'Task not found'"""
        repo = MemoryRepository()

        # Mock inputs: invalid task_id
        inputs = iter(["invalid-id"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        update_task_operation(repo)

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()


class TestUpdateWithEnterKeyKeepsValue:
    """Test update with Enter key keeps current value (T056 - P3.6)"""

    def test_update_with_enter_keeps_current_value(self, monkeypatch, capsys):
        """Pressing Enter keeps current title/description"""
        repo = MemoryRepository()
        task = Task(title="Original title", description="Original description")
        repo.add(task)

        # Mock inputs: task_id, empty (keep title), empty (keep description)
        inputs = iter([task.id[:8], "", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        update_task_operation(repo)

        # Verify values unchanged
        updated_task = repo.get(task.id)
        assert updated_task.title == "Original title"
        assert updated_task.description == "Original description"


class TestUpdateCompletedTaskAllowed:
    """Test update completed task allowed (T057 - P3.7)"""

    def test_update_completed_task_allowed(self, monkeypatch, capsys):
        """Updating a completed task is allowed"""
        repo = MemoryRepository()
        task = Task(title="Original title")
        task.mark_complete()
        repo.add(task)

        # Mock inputs: task_id, new_title, empty
        inputs = iter([task.id[:8], "Updated title", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        update_task_operation(repo)

        # Verify update succeeded
        updated_task = repo.get(task.id)
        assert updated_task.title == "Updated title"
        assert updated_task.status == "complete"  # Status remains complete


class TestUpdateCancellation:
    """Test update cancellation with Ctrl+C (T058 - P3.8)"""

    def test_update_cancellation_with_keyboard_interrupt(self, monkeypatch, capsys):
        """Ctrl+C during update displays 'Operation cancelled'"""
        repo = MemoryRepository()
        task = Task(title="Original title")
        repo.add(task)

        # Mock inputs: task_id, then KeyboardInterrupt
        def mock_input(prompt):
            if "task ID" in prompt:
                return task.id[:8]
            raise KeyboardInterrupt

        monkeypatch.setattr('builtins.input', mock_input)

        update_task_operation(repo)

        captured = capsys.readouterr()
        assert "cancelled" in captured.out.lower()
