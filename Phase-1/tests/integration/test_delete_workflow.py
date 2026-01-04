"""
Integration tests for Delete Task workflow (User Story 5).

Tests cover:
- T071-T075: Delete task integration tests

User Story P5: User wants to remove tasks permanently
"""

import pytest
from src.domain.task import Task
from src.storage.memory_repository import MemoryRepository
from src.cli.operations import delete_task_operation


class TestDeleteTaskWithConfirmation:
    """Test delete task with confirmation (T071 - P5.1)"""

    def test_delete_task_with_yes_confirmation(self, monkeypatch, capsys):
        """Delete task with 'y' confirmation succeeds"""
        repo = MemoryRepository()
        task = Task(title="Task to delete")
        repo.add(task)

        # Mock inputs: task_id, 'y' confirmation
        inputs = iter([task.id[:8], 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        delete_task_operation(repo)

        # Verify task deleted
        assert repo.get(task.id) is None

        # Verify success message
        captured = capsys.readouterr()
        assert "✓" in captured.out or "deleted successfully" in captured.out


class TestDeleteTaskWithDeclination:
    """Test delete task with declination (T072 - P5.2)"""

    def test_delete_task_with_no_declination(self, monkeypatch, capsys):
        """Delete task with 'n' declination cancels operation"""
        repo = MemoryRepository()
        task = Task(title="Task not to delete")
        repo.add(task)

        # Mock inputs: task_id, 'n' declination
        inputs = iter([task.id[:8], 'n'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        delete_task_operation(repo)

        # Verify task NOT deleted
        assert repo.get(task.id) is not None

        # Verify cancellation message
        captured = capsys.readouterr()
        assert "cancelled" in captured.out.lower()


class TestDeleteWithInvalidID:
    """Test delete with invalid task ID (T073 - P5.3)"""

    def test_delete_with_invalid_id_shows_error(self, monkeypatch, capsys):
        """Delete with invalid ID displays 'Task not found'"""
        repo = MemoryRepository()

        # Mock inputs: invalid task_id
        inputs = iter(["invalid-id"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        delete_task_operation(repo)

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()


class TestDeleteLastTask:
    """Test delete last task makes list empty (T074 - P5.4)"""

    def test_delete_last_task_makes_list_empty(self, monkeypatch, capsys):
        """Deleting the last task makes repository empty"""
        repo = MemoryRepository()
        task = Task(title="Only task")
        repo.add(task)

        # Mock inputs: task_id, 'y' confirmation
        inputs = iter([task.id[:8], 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        delete_task_operation(repo)

        # Verify repository empty
        assert len(repo.get_all()) == 0


class TestDeleteCompletedTask:
    """Test delete completed task allowed (T075 - P5.5)"""

    def test_delete_completed_task_allowed(self, monkeypatch, capsys):
        """Deleting a completed task is allowed"""
        repo = MemoryRepository()
        task = Task(title="Completed task")
        task.mark_complete()
        repo.add(task)

        # Mock inputs: task_id, 'y' confirmation
        inputs = iter([task.id[:8], 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        delete_task_operation(repo)

        # Verify task deleted
        assert repo.get(task.id) is None
