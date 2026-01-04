"""
Integration tests for Mark Complete workflow (User Story 4).

Tests cover:
- T063-T067: Mark complete integration tests

User Story P4: User wants to mark tasks as done
"""

import pytest
from src.domain.task import Task
from src.storage.memory_repository import MemoryRepository
from src.cli.operations import mark_complete_operation


class TestMarkPendingTaskComplete:
    """Test mark pending task complete (T063 - P4.1)"""

    def test_mark_pending_task_complete(self, monkeypatch, capsys):
        """Mark pending task as complete succeeds"""
        repo = MemoryRepository()
        task = Task(title="Pending task")
        repo.add(task)

        # Mock inputs: task_id
        inputs = iter([task.id[:8]])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        mark_complete_operation(repo)

        # Verify task marked complete
        completed_task = repo.get(task.id)
        assert completed_task.status == "complete"
        assert completed_task.completed_at is not None

        # Verify success message
        captured = capsys.readouterr()
        assert "✓" in captured.out or "complete" in captured.out


class TestMarkCompleteTaskAgainRejected:
    """Test mark complete task again rejected (T064 - P4.2)"""

    def test_mark_complete_task_again_shows_error(self, monkeypatch, capsys):
        """Marking already-complete task displays error"""
        repo = MemoryRepository()
        task = Task(title="Already complete task")
        task.mark_complete()
        repo.add(task)

        # Mock inputs: task_id
        inputs = iter([task.id[:8]])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        mark_complete_operation(repo)

        # Verify error message
        captured = capsys.readouterr()
        assert "✗" in captured.out or "already complete" in captured.out.lower()


class TestMarkCompleteWithInvalidID:
    """Test mark complete with invalid task ID (T065 - P4.3)"""

    def test_mark_complete_with_invalid_id_shows_error(self, monkeypatch, capsys):
        """Mark complete with invalid ID displays 'Task not found'"""
        repo = MemoryRepository()

        # Mock inputs: invalid task_id
        inputs = iter(["invalid-id"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        mark_complete_operation(repo)

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()


class TestCompleteTaskShowsCheckInList:
    """Test complete task shows [✓] in list (T066 - P4.4)"""

    def test_complete_task_shows_check_indicator_in_list(self, monkeypatch, capsys):
        """Completed task shows [✓] in view_all_tasks"""
        from src.cli.operations import view_all_tasks_operation

        repo = MemoryRepository()
        task = Task(title="Completed task")
        task.mark_complete()
        repo.add(task)

        # Mock input for "view details" prompt (press Enter to skip)
        monkeypatch.setattr('builtins.input', lambda _: "")

        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "[✓]" in captured.out


class TestMarkOneTaskComplete:
    """Test mark one task complete, others unchanged (T067 - P4.5)"""

    def test_mark_one_task_complete_others_unchanged(self, monkeypatch, capsys):
        """Marking one task complete does not affect other tasks"""
        repo = MemoryRepository()

        # Create 3 tasks
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        task3 = Task(title="Task 3")
        repo.add(task1)
        repo.add(task2)
        repo.add(task3)

        # Mark task2 complete
        inputs = iter([task2.id[:8]])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        mark_complete_operation(repo)

        # Verify only task2 is complete
        assert repo.get(task1.id).status == "pending"
        assert repo.get(task2.id).status == "complete"
        assert repo.get(task3.id).status == "pending"
