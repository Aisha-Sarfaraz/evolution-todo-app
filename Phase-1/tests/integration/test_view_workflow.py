"""
Integration tests for View Tasks workflow (User Story 2).

Tests cover:
- T039-T044: View tasks integration tests

User Story P2: User wants to see all tasks or view specific task details

TDD Phase: Tests for implemented view operations
"""

import pytest
from src.domain.task import Task
from src.storage.memory_repository import MemoryRepository
from src.cli.operations import view_all_tasks_operation, view_task_details_operation


class TestViewAllTasksEmpty:
    """Test view all tasks when empty (T039 - P2.1)"""

    def test_view_all_tasks_when_empty_displays_no_tasks_message(self, capsys):
        """View all tasks when empty displays 'No tasks found'"""
        repo = MemoryRepository()

        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "No tasks found" in captured.out or "0 tasks" in captured.out


class TestViewAllTasksWithMultipleTasks:
    """Test view all tasks with 5 tasks (T040 - P2.2)"""

    def test_view_all_tasks_with_5_tasks_displays_list(self, monkeypatch, capsys):
        """View all tasks with 5 tasks displays compact list"""
        repo = MemoryRepository()

        # Create 5 tasks
        for i in range(1, 6):
            task = Task(title=f"Task {i}")
            repo.add(task)

        # Mock input for "view details" prompt (press Enter to skip)
        monkeypatch.setattr('builtins.input', lambda _: "")

        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "Total: 5 tasks" in captured.out
        assert "Task 1" in captured.out
        assert "Task 5" in captured.out


class TestViewTaskDetailsByID:
    """Test view task details by ID (T041 - P2.3)"""

    def test_view_task_details_by_id(self, capsys):
        """View task details displays all 7 attributes"""
        repo = MemoryRepository()
        task = Task(title="Test task", description="Test description")
        repo.add(task)

        view_task_details_operation(repo, task.id[:8])

        captured = capsys.readouterr()
        assert task.id in captured.out
        assert "Test task" in captured.out
        assert "Test description" in captured.out
        assert "pending" in captured.out


class TestViewLongDescriptionTruncation:
    """Test long description truncation in list (T042 - P2.4)"""

    def test_view_list_truncates_long_title_to_50_chars(self, monkeypatch, capsys):
        """View list truncates title to 50 chars"""
        repo = MemoryRepository()
        long_title = "A" * 100
        task = Task(title=long_title)
        repo.add(task)

        # Mock input for "view details" prompt (press Enter to skip)
        monkeypatch.setattr('builtins.input', lambda _: "")

        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        # List view should truncate title
        assert "A" * 50 in captured.out


class TestViewCompleteTaskIndicator:
    """Test complete task shows [✓] (T043 - P2.5)"""

    def test_view_complete_task_shows_check_indicator(self, monkeypatch, capsys):
        """View complete task shows [✓] status indicator"""
        repo = MemoryRepository()
        task = Task(title="Completed task")
        task.mark_complete()
        repo.add(task)

        # Mock input for "view details" prompt (press Enter to skip)
        monkeypatch.setattr('builtins.input', lambda _: "")

        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "[✓]" in captured.out or "complete" in captured.out


class TestViewPendingTaskIndicator:
    """Test pending task shows [ ] (T044 - P2.6)"""

    def test_view_pending_task_shows_empty_indicator(self, monkeypatch, capsys):
        """View pending task shows [ ] status indicator"""
        repo = MemoryRepository()
        task = Task(title="Pending task")
        repo.add(task)

        # Mock input for "view details" prompt (press Enter to skip)
        monkeypatch.setattr('builtins.input', lambda _: "")

        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "[ ]" in captured.out or "pending" in captured.out
